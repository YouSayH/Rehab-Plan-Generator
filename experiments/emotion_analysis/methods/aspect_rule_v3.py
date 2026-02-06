import spacy
from .base import BaseAnalyzer

class AspectRuleAnalyzerV3(BaseAnalyzer):
    def __init__(self):
        print("[V3] Loading GiNZA (Vector)...")
        try: self.nlp = spacy.load("ja_ginza")
        except: self.nlp = None
        self.direct = {"笑顔": 1, "拒否": -1, "不穏": -1, "不満": -1}
        self.contextual = {"良い": 1, "良好": 1, "悪い": -1, "ない": -1, "低下": -1, "困難": -1}
        self.seeds = ["意欲", "リハビリ", "訓練", "感情"]
        if self.nlp: self.vecs = [self.nlp(w)[0] for w in self.seeds if self.nlp(w)[0].has_vector]
        self.negations = {"ない", "ず", "なし"}

    def _is_target(self, t):
        return t.pos_ in ["NOUN","PROPN"] and t.has_vector and any(t.similarity(s)>0.6 for s in self.vecs)

    def analyze(self, text: str):
        if not self.nlp: return {"error": "No GiNZA"}
        doc = self.nlp(text)
        score = 0; details = []
        for token in doc:
            lemma = token.lemma_; val = 0; trigger = ""
            if lemma in self.direct: val = self.direct[lemma]
            elif lemma in self.contextual:
                if self._is_target(token.head) or any(self._is_target(c) for c in token.children):
                    val = self.contextual[lemma]
            if val != 0:
                is_neg = any(c.lemma_ in self.negations for c in token.children) or token.head.lemma_ in self.negations
                final = val * -1 if is_neg else val
                score += final
                details.append(f"{lemma}({final})")
        return {"method": "V3 (Vector)", "score": max(min(score, 1), -1), "details": details}
