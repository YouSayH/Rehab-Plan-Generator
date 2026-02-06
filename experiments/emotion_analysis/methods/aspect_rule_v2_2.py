import spacy
from .base import BaseAnalyzer

class AspectRuleAnalyzerV2_2(BaseAnalyzer):
    def __init__(self):
        print("[AspectRuleV2.2] Loading GiNZA (Recursive & Sibling Negation)...")
        try: self.nlp = spacy.load("ja_ginza")
        except: self.nlp = None

        # A. 直接判定語 (Target不問)
        # "覇気" など、それ自体が良い意味を持つ名詞も含める
        self.direct_indicators = {
            "笑顔": 1, "意欲的": 1, "積極的": 1, "自発的": 1, "楽しむ": 1, "活気": 1, "穏やか": 1, "覇気": 1,
            "拒否": -1, "不穏": -1, "怒る": -1, "泣く": -1, "嫌がる": -1, "不満": -1, "興奮": -1, "拒絶": -1
        }

        # B. 文脈判定語 (Target確認が必要)
        self.contextual_indicators = {
            "良い": 1, "良好": 1, "高い": 1, "ある": 1, "できる": 1, "スムーズ": 1, "保つ": 1,
            "悪い": -1, "ない": -1, "低い": -1, "困難": -1, "低下": -1, "不可": -1, "乏しい": -1, 
            "られない": -1, "難渋": -1, "見られない": -1
        }

        # C. ターゲット語
        self.targets = {
            "意欲", "気力", "やる気", "モチベーション", 
            "表情", "顔色", "発言", "言動", "態度", "声",
            "リハビリ", "訓練", "練習", "自主トレ", "離床", "参加",
            "メンタル", "精神", "活気"
        }
        
        # D. 中継地点ワード (Passthrough)
        self.passthrough_nouns = {"状態", "様子", "感じ", "傾向", "印象", "見受け", "状況"}

        self.negations = {"ない", "ず", "なし", "ありません", "ぬ", "ん"}

    def _find_target_recursive(self, token, depth=0):
        """再帰的にターゲットを探す"""
        if depth > 2: return None # ループ防止

        # 1. 自分がターゲットならOK
        if token.lemma_ in self.targets:
            return token.lemma_
        
        # 2. 自分が「状態」等の場合、その修飾語(children)を探す
        # 例: [メンタル] --(nmod)--> [状態]
        if token.lemma_ in self.passthrough_nouns:
            for child in token.children:
                found = self._find_target_recursive(child, depth + 1)
                if found: return found
        
        return None

    def analyze(self, text: str):
        if not self.nlp: return {"error": "No GiNZA"}
        doc = self.nlp(text)
        score = 0; details = []
        
        for token in doc:
            lemma = token.lemma_
            val = 0; trigger_type = ""; target_word = ""

            # Pattern A: Direct
            if lemma in self.direct_indicators:
                val = self.direct_indicators[lemma]
                trigger_type = "Direct"
                target_word = lemma

            # Pattern B: Contextual
            elif lemma in self.contextual_indicators:
                found_target = None
                
                # 1. 親方向チェック (例: 意欲(head) が ある(token))
                found_target = self._find_target_recursive(token.head)
                
                # 2. 子方向チェック (例: 良い(token) 傾向(child))
                if not found_target:
                    for c in token.children:
                        res = self._find_target_recursive(c)
                        if res: 
                            found_target = res
                            break
                
                if found_target:
                    val = self.contextual_indicators[lemma]
                    trigger_type = "Context"
                    target_word = found_target

            # Score Calculation
            if val != 0:
                is_neg = False
                
                # 1. 自分の子供に否定 (意欲がない)
                if any(c.lemma_ in self.negations for c in token.children): is_neg = True
                
                # 2. 自分の親が否定 (参加できない)
                if token.head.lemma_ in self.negations: is_neg = True

                # 3. 【V2.2追加】親の子供(兄弟)に否定 (覇気が 感じ られない)
                # Token(覇気/Subject) -> Head(感じ/Verb) <- Sibling(ない/Aux)
                if trigger_type == "Direct":
                     for sibling in token.head.children:
                        if sibling.lemma_ in self.negations: is_neg = True

                # 4. 複合語内否定
                if "ない" in lemma or "ず" in lemma: is_neg = True

                final_val = val * -1 if is_neg else val
                score += final_val
                
                neg_str = "(Neg)" if is_neg else ""
                details.append(f"[{target_word}]{lemma}{neg_str}({final_val})")

        final = max(min(score, 1.0), -1.0)
        label = "NEUTRAL"
        if final > 0: label = "POSITIVE"
        if final < 0: label = "NEGATIVE"
        return {"method": "Aspect Rule V2.2", "score": final, "label": label, "details": details}