import spacy
from .base import BaseAnalyzer

class AspectRuleAnalyzer(BaseAnalyzer):
    def __init__(self):
        print("[AspectRule] Loading GiNZA...")
        try: self.nlp = spacy.load("ja_ginza")
        except: self.nlp = None
        self.targets = {"意欲", "気力", "やる気", "表情", "発言", "態度", "リハビリ", "訓練"}
        self.polarity = {"良い": 1, "意欲的": 1, "笑顔": 1, "悪い": -1, "拒否": -1, "困難": -1, "低下": -1, "不穏": -1}
        self.negations = {"ない", "ず", "なし"}

    def analyze(self, text: str):
        if not self.nlp: return {"error": "No GiNZA"}
        doc = self.nlp(text)
        score = 0; details = []
        
        for token in doc:
            if token.lemma_ in self.polarity:
                val = self.polarity[token.lemma_]
                # ターゲット探索
                target = None
                if token.head.lemma_ in self.targets: target = token.head.lemma_
                for c in token.children:
                    if c.lemma_ in self.targets: target = c.lemma_
                
                if target:
                    # 否定チェック
                    is_neg = any(c.lemma_ in self.negations for c in token.children)
                    final_val = val * -1 if is_neg else val
                    score += final_val
                    details.append(f"[{target}]-{token.lemma_}({final_val})")
        
        final = max(min(score, 1.0), -1.0)
        return {
            "method": "Aspect Rule",
            "score": final,
            "label": "POSITIVE" if final > 0 else "NEGATIVE" if final < 0 else "NEUTRAL",
            "details": details
        }
