import spacy
from .base import BaseAnalyzer

class RuleBasedAnalyzer(BaseAnalyzer):
    def __init__(self):
        print("[Rule] Loading GiNZA...")
        try: self.nlp = spacy.load("ja_ginza")
        except: self.nlp = None

    def analyze(self, text: str):
        if not self.nlp: return {"error": "No GiNZA"}
        doc = self.nlp(text)
        score = 0
        details = []
        # 簡易辞書
        pos = {"意欲", "笑顔", "自発的", "良好"}
        neg = {"拒否", "困難", "疲労", "不穏", "中断"}
        
        for token in doc:
            w = token.lemma_
            if w in pos:
                score += 1; details.append(f"{w}(+1)")
            elif w in neg:
                score -= 1; details.append(f"{w}(-1)")
        
        final = max(min(score, 1.0), -1.0)
        return {
            "method": "Rule (Simple)", 
            "score": final, 
            "label": "POSITIVE" if final > 0 else "NEGATIVE" if final < 0 else "NEUTRAL",
            "details": details
        }
