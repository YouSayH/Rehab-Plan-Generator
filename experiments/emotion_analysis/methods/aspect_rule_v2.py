import spacy
from .base import BaseAnalyzer

class AspectRuleAnalyzerV2(BaseAnalyzer):
    def __init__(self):
        print("[V2] Loading GiNZA...")
        try: self.nlp = spacy.load("ja_ginza")
        except: self.nlp = None
        self.direct_indicators = {"笑顔": 1, "意欲的": 1, "積極的": 1, "拒否": -1, "不穏": -1, "嫌がる": -1, "不満": -1}
        self.contextual_indicators = {"良い": 1, "良好": 1, "ある": 1, "できる": 1, "悪い": -1, "ない": -1, "低下": -1, "困難": -1}
        self.targets = {"意欲", "気力", "やる気", "リハビリ", "訓練", "練習", "参加"}
        self.negations = {"ない", "ず", "なし", "ありません", "ぬ"}

    def analyze(self, text: str):
        if not self.nlp: return {"error": "No GiNZA"}
        doc = self.nlp(text)
        score = 0; details = []
        for token in doc:
            lemma = token.lemma_; val = 0; trigger = ""
            if lemma in self.direct_indicators:
                val = self.direct_indicators[lemma]; trigger = "Direct"
            elif lemma in self.contextual_indicators:
                is_related = (token.head.lemma_ in self.targets) or any(c.lemma_ in self.targets for c in token.children)
                if is_related: val = self.contextual_indicators[lemma]; trigger = "Context"
            if val != 0:
                is_neg = any(c.lemma_ in self.negations for c in token.children) or token.head.lemma_ in self.negations
                final = val * -1 if is_neg else val
                score += final
                details.append(f"{lemma}({final})")
        return {"method": "V2 (Strict)", "score": max(min(score, 1), -1), "details": details}
