import os
import time
from google import genai
from ollama import Client as OllamaClient
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class AIEngine:
    def __init__(self):
        """
        Initializes the 2026 Tri-Tier Engine: 
        1. Cloud (Gemini) - Logic/Judgment
        2. LPU (Groq) - High-speed inference
        3. Local (Ollama) - Privacy/Edge compute
        """
        # 1. Google Gemini Client (Frontier Reasoning)
        self.gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # 2. Ollama Client (Local Privacy)
        self.ollama_client = OllamaClient()

        # 3. Groq Client (Ultra-fast LPU inference)
        self.groq_client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

    def query_gemini(self, model_id="gemini-2.0-flash", prompt=""):
        """Calls Google Cloud's Frontier Models with full usage metadata."""
        try:
            start_time = time.time()
            response = self.gemini_client.models.generate_content(
                model=model_id,
                contents=prompt
            )
            latency = time.time() - start_time
            return {
                "text": response.text,
                "latency": f"{latency:.2f}s",
                "tokens": response.usage_metadata.total_token_count,
                "provider": "Google Cloud"
            }
        except Exception as e:
            return {"text": f"Gemini Error: {str(e)[:50]}...", "latency": "0s", "tokens": 0, "provider": "Google (Fail)"}

    def query_groq(self, model_id="llama-3.3-70b-versatile", prompt=""):
        """Calls Groq's LPU for sub-second responses."""
        try:
            start_time = time.time()
            response = self.groq_client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}]
            )
            latency = time.time() - start_time
            return {
                "text": response.choices[0].message.content,
                "latency": f"{latency:.2f}s",
                "tokens": response.usage.total_tokens,
                "provider": "Groq LPU"
            }
        except Exception as e:
            return {"text": f"Groq Error: {str(e)[:50]}...", "latency": "0s", "tokens": 0, "provider": "Groq (Fail)"}

    def query_ollama(self, model_id="qwen2.5:0.5b", prompt=""):
        """Calls Local Compute. No API key needed, data never leaves your RAM."""
        try:
            start_time = time.time()
            response = self.ollama_client.generate(model=model_id, prompt=prompt)
            latency = time.time() - start_time
            
            # eval_count is the number of tokens generated in the response
            tokens = response.get('eval_count', 0)
            
            return {
                "text": response['response'],
                "latency": f"{latency:.2f}s",
                "tokens": tokens,
                "provider": "Local (Ollama)"
            }
        except Exception as e:
            return {"text": f"Ollama Error: {e}", "latency": "0s", "tokens": 0, "provider": "Ollama (Fail)"}

    def query(self, provider, prompt, model=None):
        """
        Unified routing method. Use this in main.py to simplify benchmarking.
        Usage: engine.query("groq", "Hello!")
        """
        if provider == "gemini":
            return self.query_gemini(model_id=model or "gemini-2.0-flash", prompt=prompt)
        elif provider == "groq":
            return self.query_groq(model_id=model or "llama-3.3-70b-versatile", prompt=prompt)
        elif provider == "local":
            return self.query_ollama(model_id=model or "qwen2.5:0.5b", prompt=prompt)
        else:
            raise ValueError(f"Unknown provider: {provider}")