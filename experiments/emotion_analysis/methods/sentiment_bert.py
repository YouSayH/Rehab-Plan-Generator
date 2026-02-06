import torch
from transformers import pipeline
from .base import BaseAnalyzer

class BertSentimentAnalyzer(BaseAnalyzer):
    def __init__(self, model_name="koheiduck/bert-japanese-finetuned-sentiment"):
        device = 0 if torch.cuda.is_available() else -1
        print(f"[BERT] Loading {model_name}...")
        try:
            self.pipe = pipeline("text-classification", model=model_name, device=device, top_k=None)
        except:
            self.pipe = None

    def analyze(self, text: str):
        if not self.pipe: return {"method": "BERT", "score": 0, "label": "ERROR"}
        results = self.pipe(text)[0]
        scores = {item["label"]: item["score"] for item in results}
        total = scores.get("POSITIVE", 0) - scores.get("NEGATIVE", 0)
        return {
            "method": "BERT (Sentiment)",
            "score": round(total, 3),
            "label": "POSITIVE" if total > 0.2 else "NEGATIVE" if total < -0.2 else "NEUTRAL",
            "details": scores
        }
