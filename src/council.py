"""
council.py - multi-model query orchestration
queries groq and ollama in parallel, synthesizes responses
"""

import concurrent.futures
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Callable

from engine import AIEngine
from auditor import Auditor, AuditResult
from memory import SovereignMemory


@dataclass
class ModelResponse:
    provider: str
    model: str
    text: str
    latency: str
    tokens: int


@dataclass 
class CouncilVerdict:
    final_response: str
    trust_score: int
    responses: list[ModelResponse]
    audit: AuditResult
    boundary_violations: list[str]


class Council:
    def __init__(
        self, 
        engine: Optional[AIEngine] = None,
        memory: Optional[SovereignMemory] = None,
        auditor: Optional[Auditor] = None,
        on_response: Optional[Callable] = None
    ):
        self.engine = engine or AIEngine()
        self.memory = memory or SovereignMemory()
        self.auditor = auditor or Auditor()
        self.on_response = on_response
        
        self.members = [
            {"name": "groq", "provider": "groq", "model": "llama-3.3-70b-versatile"},
            {"name": "local", "provider": "local", "model": "qwen2.5-coder:1.5b-base"},
        ]
    
    def _query_member(self, member: dict, prompt: str) -> ModelResponse:
        try:
            result = self.engine.query(
                provider=member["provider"],
                prompt=prompt,
                model=member["model"]
            )
            
            response = ModelResponse(
                provider=member["name"],
                model=member["model"],
                text=result.get("text", "no response"),
                latency=result.get("latency", "0s"),
                tokens=result.get("tokens", 0)
            )
            
            if self.on_response:
                self.on_response(response)
            
            return response
            
        except Exception as e:
            return ModelResponse(
                provider=member["name"],
                model=member["model"],
                text=f"error: {str(e)[:100]}",
                latency="0s",
                tokens=0
            )
    
    def query_all(self, prompt: str) -> list[ModelResponse]:
        responses = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self._query_member, m, prompt): m
                for m in self.members
            }
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    responses.append(future.result(timeout=30))
                except Exception as e:
                    member = futures[future]
                    responses.append(ModelResponse(
                        provider=member["name"],
                        model=member["model"],
                        text=f"timeout: {str(e)[:50]}",
                        latency="30s+",
                        tokens=0
                    ))
        
        return responses
    
    def synthesize(self, prompt: str, responses: list[ModelResponse]) -> str:
        valid = [r for r in responses if not r.text.startswith("error") and not r.text.startswith("timeout")]
        
        if not valid:
            return "both models failed to respond. try again?"
        
        if len(valid) == 1:
            return valid[0].text
        
        groq_resp = next((r for r in valid if r.provider == "groq"), None)
        if groq_resp:
            return groq_resp.text
        
        return valid[0].text
    
    def deliberate(self, prompt: str) -> CouncilVerdict:
        # Semantic Boundary Check
        boundary_violations = self.memory.check_boundary(prompt)
        violated_texts = [v["boundary_text"] for v in boundary_violations]
        
        # Initial Construction
        # If hit a boundary, immediately steer the models
        current_prompt = prompt
        if boundary_violations:
            current_prompt = f"USER BOUNDARY ALERT: The user has strictly rejected: {violated_texts}. Original request: {prompt}. Provide an alternative that respects these boundaries."
        
        # Query the Council
        responses = self.query_all(current_prompt)
        final_response = self.synthesize(current_prompt, responses)
        
        # Linguistic Audit (The Conscience)
        audit = self.auditor.score_response(final_response, prompt)
        
        # If the score is < 50, the Council failed. Force a rewrite before the user sees it.
        if audit.score < 50:
            correction_prompt = (
                f"CRITICAL ALIGNMENT FAILURE. Your previous response scored {audit.score}% on a non-coercion audit. "
                f"Reasoning: {audit.reasoning}. "
                f"Constraint: You must help the user with '{prompt}' WITHOUT using any coercive or hustle-culture language. "
                f"REWRITE now."
            )
            # Second attempt
            responses = self.query_all(correction_prompt)
            final_response = self.synthesize(correction_prompt, responses)
            # Re-audit the second attempt
            audit = self.auditor.score_response(final_response, prompt)
        
        # Final Regex Guardrail (The Hardware Filter)
        if audit.verdict == "override":
            final_response = self.auditor.filter_coercion(final_response)
        
        return CouncilVerdict(
            final_response=final_response,
            trust_score=audit.score,
            responses=responses,
            audit=audit,
            boundary_violations=violated_texts
        )


if __name__ == "__main__":
    council = Council()
    verdict = council.deliberate("help me design an efficient morning routine")
    
    print(f"trust: {verdict.trust_score}%")
    print(f"response: {verdict.final_response[:300]}...")
    
    for r in verdict.responses:
        print(f"[{r.provider}] ({r.latency}): {r.text[:100]}...")
