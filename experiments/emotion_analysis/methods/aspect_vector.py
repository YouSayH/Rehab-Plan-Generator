import spacy
from .base import BaseAnalyzer

class VectorAspectAnalyzer(BaseAnalyzer):
    def __init__(self):
        print("[VectorAspect] Loading GiNZA(Vector)...")
        try: 
            self.nlp = spacy.load("ja_ginza")
            self.seeds = [self.nlp(w)[0] for w in ["意欲", "感情", "態度", "訓練"]]
        except: self.nlp = None
        self.polarity = {"良い": 1, "意欲的": 1, "笑顔": 1, "悪い": -1, "拒否": -1, "困難": -1, "低下": -1}
        self.negations = {"ない", "ず", "なし"}

    def _is_target(self, token):
        if not token.has_vector or token.pos_ not in ["NOUN", "PROPN"]: return False
        return any(token.similarity(s) > 0.55 for s in self.seeds)

    def analyze(self, text: str):
        if not self.nlp: return {"error": "No GiNZA"}
        doc = self.nlp(text)
        score = 0; details = []
        
        for token in doc:
            if token.lemma_ in self.polarity:
                val = self.polarity[token.lemma_]
                target = None
                # 親または子がターゲット(類似語含む)か？
                if self._is_target(token.head): target = token.head
                for c in token.children:
                    if self._is_target(c): target = c
                
                if target:
                    is_neg = any(c.lemma_ in self.negations for c in token.children)
                    final_val = val * -1 if is_neg else val
                    score += final_val
                    details.append(f"[{target.text}]-{token.lemma_}({final_val})")

        final = max(min(score, 1.0), -1.0)
        return {
            "method": "Vector Aspect",
            "score": final,
            "label": "POSITIVE" if final > 0 else "NEGATIVE" if final < 0 else "NEUTRAL",
            "details": details
        }
