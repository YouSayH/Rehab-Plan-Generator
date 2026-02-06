import json
import requests
from .base import BaseAnalyzer

class OllamaAnalyzer(BaseAnalyzer):
    def __init__(self, model_name="hf.co/unsloth/LFM2.5-1.2B-Instruct-GGUF:Q4_K_M"):
        self.model = model_name
        self.url = "http://localhost:11434/api/generate"

    def analyze(self, text: str):
        prompt = f"Analyze clinical text. Output JSON with score(-1.0 to 1.0) and reason.\nText: {text}\nJSON:"
        try:
            res = requests.post(self.url, json={"model": self.model, "prompt": prompt, "format": "json", "stream": False})
            if res.status_code != 200: return {"method": "Ollama", "score": 0, "details": "Connection Error"}
            data = json.loads(res.json()["response"])
            score = float(data.get("score", 0))
            return {
                "method": f"Ollama ({self.model})",
                "score": score,
                "label": "POSITIVE" if score > 0.2 else "NEGATIVE" if score < -0.2 else "NEUTRAL",
                "details": data.get("reason", "")
            }
        except: return {"method": "Ollama", "score": 0, "details": "Error"}
