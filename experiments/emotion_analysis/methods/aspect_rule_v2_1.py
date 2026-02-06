import spacy
from .base import BaseAnalyzer

class AspectRuleAnalyzerV2_1(BaseAnalyzer):
    def __init__(self):
        print("[AspectRuleV2.1] Loading GiNZA with Recursive Search...")
        try: self.nlp = spacy.load("ja_ginza")
        except: self.nlp = None

        # A. 直接判定語
        self.direct_indicators = {
            "笑顔": 1, "意欲的": 1, "積極的": 1, "自発的": 1, "楽しむ": 1,
            "拒否": -1, "不穏": -1, "怒る": -1, "泣く": -1, "嫌がる": -1, "不満": -1,
            "覇気": 1 # 「覇気」自体が良い言葉なのでDirectに入れても良いが、今回はテストのためContextでも拾えるように調整
        }

        # B. 文脈判定語
        self.contextual_indicators = {
            "良い": 1, "良好": 1, "高い": 1, "ある": 1, "できる": 1, 
            "悪い": -1, "ない": -1, "低い": -1, "困難": -1, "低下": -1, "不可": -1, "乏しい": -1, "られない": -1
        }

        # C. ターゲット辞書 (メンタル、覇気を追加)
        self.targets = {
            "意欲", "気力", "やる気", "リハビリ", "訓練", "練習", "参加",
            "メンタル", "精神", "覇気", "活気"
        }
        
        # D. 中継地点ワード (これらが主語なら、その修飾語まで見に行く)
        self.passthrough_nouns = {"状態", "様子", "感じ", "傾向", "印象"}

        self.negations = {"ない", "ず", "なし", "ありません", "ぬ"}

    def _find_target_recursive(self, token, depth=0):
        """再帰的にターゲットを探す"""
        if depth > 1: return None # 深追いしすぎない

        # 1. 自分がターゲットならOK
        if token.lemma_ in self.targets:
            return token.lemma_
        
        # 2. 自分が「状態」などの抽象名詞なら、その子供(修飾語)を探す
        # 例: [メンタル] -> (nmod) -> [状態]
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
                
                # Head check (親を見る)
                found_target = self._find_target_recursive(token.head)
                
                # Children check (子を見る)
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
                # 否定チェック (自分以下、または親)
                for c in token.children:
                    if c.lemma_ in self.negations: is_neg = True
                if token.head.lemma_ in self.negations: is_neg = True
                # 「感じられない」のように一語として扱われる場合の補助
                if "ない" in lemma or "ず" in lemma: is_neg = True

                final_val = val * -1 if is_neg else val
                score += final_val
                
                neg_str = "(Neg)" if is_neg else ""
                details.append(f"[{target_word}]{lemma}{neg_str}({final_val})")

        final = max(min(score, 1.0), -1.0)
        label = "NEUTRAL"
        if final > 0: label = "POSITIVE"
        if final < 0: label = "NEGATIVE"
        return {"method": "Aspect Rule V2.1", "score": final, "label": label, "details": details}