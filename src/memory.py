"""
memory.py - Sovereign Memory System for rei
Uses ChromaDB to store user boundaries (rejected suggestions).
rei never crosses a boundary twice.
"""

import chromadb
from chromadb.config import Settings
from datetime import datetime
import os
import hashlib


class SovereignMemory:
    """
    ChromaDB-based memory that stores user boundaries.
    When the user rejects an AI suggestion, it becomes a "boundary"
    that rei will respect in all future interactions.
    """
    
    def __init__(self, persist_dir: str = "data/chroma_db"):
        """Initialize ChromaDB with persistent storage."""
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Collection for storing boundaries (rejected suggestions)
        self.boundaries = self.client.get_or_create_collection(
            name="boundaries",
            metadata={"description": "User-defined boundaries - things REI must never suggest again"}
        )
        
        # Collection for storing conversation context
        self.context = self.client.get_or_create_collection(
            name="context",
            metadata={"description": "Conversation history for contextual awareness"}
        )
    
    def _generate_id(self, text: str) -> str:
        """Generate a unique ID based on text content."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def add_boundary(self, rejection_text: str, context: str = "", severity: str = "firm") -> str:
        """
        Store a user rejection as a boundary.
        
        Args:
            rejection_text: What the user rejected (e.g., "working overtime")
            context: The situation when rejection occurred
            severity: How firm the boundary is (soft, firm, absolute)
        
        Returns:
            The ID of the stored boundary
        """
        boundary_id = f"boundary_{self._generate_id(rejection_text)}"
        timestamp = datetime.now().isoformat()
        
        self.boundaries.upsert(
            ids=[boundary_id],
            documents=[rejection_text],
            metadatas=[{
                "context": context,
                "severity": severity,
                "timestamp": timestamp,
                "times_checked": 0
            }]
        )
        
        return boundary_id
    
    def check_boundary(self, prompt: str, threshold: float = 0.7) -> list[dict]:
        """
        Check if a prompt might violate any stored boundaries.
        
        Args:
            prompt: The user's current request
            threshold: Similarity threshold (lower = more strict)
        
        Returns:
            List of potentially violated boundaries with similarity scores
        """
        if self.boundaries.count() == 0:
            return []
        
        results = self.boundaries.query(
            query_texts=[prompt],
            n_results=min(5, self.boundaries.count())
        )
        
        violations = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                distance = results['distances'][0][i] if results['distances'] else 1.0
                # ChromaDB returns L2 distance, convert to similarity
                similarity = 1 / (1 + distance)
                
                if similarity >= threshold:
                    violations.append({
                        "boundary_id": results['ids'][0][i],
                        "boundary_text": doc,
                        "similarity": similarity,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {}
                    })
        
        return violations
    
    def get_all_boundaries(self) -> list[dict]:
        """Retrieve all stored boundaries for UI display."""
        if self.boundaries.count() == 0:
            return []
        
        results = self.boundaries.get()
        
        boundaries = []
        for i, doc in enumerate(results['documents']):
            boundaries.append({
                "id": results['ids'][i],
                "text": doc,
                "metadata": results['metadatas'][i] if results['metadatas'] else {}
            })
        
        return boundaries
    
    def remove_boundary(self, boundary_id: str) -> bool:
        """Remove a boundary if user changes their mind."""
        try:
            self.boundaries.delete(ids=[boundary_id])
            return True
        except Exception:
            return False
    
    def add_context(self, role: str, content: str, session_id: str = "default") -> None:
        """Store conversation context for continuity."""
        context_id = f"ctx_{session_id}_{self._generate_id(content)}"
        timestamp = datetime.now().isoformat()
        
        self.context.upsert(
            ids=[context_id],
            documents=[content],
            metadatas=[{
                "role": role,
                "session_id": session_id,
                "timestamp": timestamp
            }]
        )
    
    def get_recent_context(self, session_id: str = "default", limit: int = 10) -> list[dict]:
        """Retrieve recent conversation context."""
        if self.context.count() == 0:
            return []
        
        results = self.context.get(
            where={"session_id": session_id},
            limit=limit
        )
        
        context_items = []
        for i, doc in enumerate(results['documents']):
            context_items.append({
                "role": results['metadatas'][i].get("role", "unknown"),
                "content": doc,
                "timestamp": results['metadatas'][i].get("timestamp", "")
            })
        
        # Sort by timestamp
        context_items.sort(key=lambda x: x['timestamp'])
        
        return context_items
    
    def clear_session(self, session_id: str = "default") -> None:
        """Clear conversation context for a session (boundaries are preserved)."""
        if self.context.count() == 0:
            return
        
        # Get all context IDs for this session
        results = self.context.get(where={"session_id": session_id})
        if results['ids']:
            self.context.delete(ids=results['ids'])
    
    def get_stats(self) -> dict:
        """Get memory statistics for UI display."""
        return {
            "total_boundaries": self.boundaries.count(),
            "total_context": self.context.count(),
            "persist_dir": self.persist_dir
        }


# Quick test
if __name__ == "__main__":
    memory = SovereignMemory()
    
    # Add a test boundary
    memory.add_boundary(
        "suggestions about working overtime or extra hours",
        context="productivity advice",
        severity="firm"
    )
    
    # Check if a prompt violates boundaries
    violations = memory.check_boundary("Can you help me be more productive by working longer hours?")
    print(f"Violations found: {violations}")
    
    # List all boundaries
    print(f"All boundaries: {memory.get_all_boundaries()}")
    print(f"Stats: {memory.get_stats()}")
