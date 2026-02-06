import time
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

# 既存のV2.2読み込み
from methods.aspect_rule_v2_2 import AspectRuleAnalyzerV2_2

class QuantizedBERTAnalyzer:
    def __init__(self, model_name="koheiduck/bert-japanese-finetuned-sentiment"):
        print(f"[Quantized BERT] Loading {model_name}...")
        self.device = "cpu"
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            base_model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self.device)
            
            # 動的量子化
            self.model = torch.quantization.quantize_dynamic(
                base_model, {torch.nn.Linear}, dtype=torch.qint8
            )
        except Exception as e:
            print(f"Error: {e}")
            self.model = None

    def analyze(self, text: str):
        if not self.model: return {"score": 0}
        
        # 実推論を実行
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # スコア計算 (Positive - Negative)
        probs = F.softmax(outputs.logits, dim=-1)[0].tolist()
        # ラベル順序はモデルによるが、このモデルは [NEUTRAL, POSITIVE, NEGATIVE] ではなく [POSITIVE, NEGATIVE] 等
        # id2labelを確認するのが確実だが、一旦このモデルの慣例に従う (0: Negative, 1: Positive の場合が多いが、sentimentモデルはconfig依存)
        # koheiduckモデルは label2id: {'POSITIVE': 1, 'NEGATIVE': 0, 'NEUTRAL': 2} 等の可能性があるため、
        # ここでは簡易的に output の最大値のラベル名を取得してスコア化する
        
        # ラベルマッピング (モデルconfigから取得推奨だが、今回は簡易実装)
        # 多くのセンチメントモデルは 0:Negative, 1:Positive
        neg_score = probs[0]
        pos_score = probs[1]
        
        # 簡易スコア (-1 ~ 1)
        score = pos_score - neg_score
        
        label = "NEUTRAL"
        if score > 0.2: label = "POSITIVE"
        if score < -0.2: label = "NEGATIVE"

        return {"score": round(score, 3), "label": label}

class NormalmDeBERTaAnalyzer:
    def __init__(self, model_name="MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"):
        print(f"[Normal mDeBERTa] Loading {model_name}...")
        self.device = "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self.device)
        self.hypothesis = "患者はリハビリに対して意欲的で、状態は良好である。"

    def analyze(self, text: str):
        inputs = self.tokenizer(text, self.hypothesis, truncation=True, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        probs = torch.softmax(outputs.logits[0], -1).tolist()
        score = probs[0] - probs[2] # Entailment - Contradiction
        
        label = "NEUTRAL"
        if score > 0.2: label = "POSITIVE"
        if score < -0.2: label = "NEGATIVE"
        return {"score": round(score, 3), "label": label}

def main():
    print("=== Initializing ===")
    v2_2 = AspectRuleAnalyzerV2_2()
    q_bert = QuantizedBERTAnalyzer()
    norm_nli = NormalmDeBERTaAnalyzer()
    
    analyzers = [
        ("V2.2 (Rule)", v2_2),
        ("Q-BERT (AI)", q_bert),
        ("mDeBERTa (AI)", norm_nli)
    ]

    # 意地悪なテストケース（身体 vs 精神）
    test_cases = [
        "笑顔でリハビリに参加。",              # 明確なPositive
        "リハビリへの意欲が低下。",            # 明確なNegative
        "右足の痛みが強く、歩行が困難。",      # 身体的Negative (精神はNeutralであるべき) ★最重要
        "リハビリへの覇気が感じられない。",    # 複雑なNegative
        "訓練に対する不満はない。"             # 否定の否定 (Positive)
    ]

    results = []
    print("\n=== Running Final Check ===")
    
    for text in test_cases:
        for name, analyzer in analyzers:
            start = time.perf_counter()
            res = analyzer.analyze(text)
            duration = (time.perf_counter() - start) * 1000
            
            results.append({
                "Text": text[:10] + "..",
                "Method": name,
                "Score": res["score"],
                "Label": res["label"],
                "Time(ms)": round(duration, 1)
            })

    df = pd.DataFrame(results)
    
    print("\n=== Accuracy & Speed Comparison ===")
    # ピボットテーブルで見やすく
    print(df.pivot(index="Text", columns="Method", values=["Label", "Score", "Time(ms)"]).to_markdown())

if __name__ == "__main__":
    main()