import torch
import time
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from .base import BaseAnalyzer

class NLIAnalyzer(BaseAnalyzer):
    def __init__(self, model_name="MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[NLI] Loading model on {self.device}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self.device)
            self.hypothesis = "患者はリハビリに対して意欲的で、状態は良好である。"
        except: self.model = None

    def analyze(self, text: str):
        if not self.model: return {"method": "NLI", "score": 0}
        
        # 計測用に処理開始
        inputs = self.tokenizer(text, self.hypothesis, truncation=True, return_tensors="pt").to(self.device)
        with torch.no_grad():
            output = self.model(inputs["input_ids"])
        probs = torch.softmax(output["logits"][0], -1).tolist()
        score = probs[0] - probs[2] # Entailment - Contradiction
        
        return {"method": "mDeBERTa (AI)", "score": round(score, 3), "details": probs}
