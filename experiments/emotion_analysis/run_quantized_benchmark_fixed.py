import time
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ルールベース読み込み
from methods.aspect_rule_v2_2 import AspectRuleAnalyzerV2_2

class QuantizedBERTAnalyzer:
    """
    mDeBERTaはPyTorch標準の動的量子化でエラーになるため、
    構造が素直なBERTモデルを使って「量子化AIの速度限界」を測定するクラス。
    """
    def __init__(self, model_name="koheiduck/bert-japanese-finetuned-sentiment"):
        print(f"[Quantized BERT] Loading {model_name}...")
        self.device = "cpu"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            base_model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self.device)
            
            # 動的量子化 (BERTなら成功する)
            print("[Quantized BERT] Applying Dynamic Quantization (float32 -> int8)...")
            self.model = torch.quantization.quantize_dynamic(
                base_model, 
                {torch.nn.Linear},
                dtype=torch.qint8
            )
            print("[Quantized BERT] Ready.")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    def analyze(self, text: str):
        if not self.model: return {"score": 0}
        
        # 推論のみ（NLIではないのでスコアの意味は異なるが、計算負荷はほぼ同じ）
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            _ = self.model(**inputs)
        
        # 速度計測用なのでダミー結果を返す
        return {"score": 0.99, "label": "BENCHMARK", "details": []}

def main():
    print("=== Initializing Models ===")
    
    # 1. ルールベース (V2.2)
    rule_v2_2 = AspectRuleAnalyzerV2_2()
    
    # 2. 量子化AI (BERT: 速度の参考)
    quantized_ai = QuantizedBERTAnalyzer()
    
    # 3. 通常AI (mDeBERTa: 重さの比較用)
    print("[Normal mDeBERTa] Loading standard model...")
    normal_tokenizer = AutoTokenizer.from_pretrained("MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7")
    normal_model = AutoModelForSequenceClassification.from_pretrained("MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7").to("cpu")

    test_cases = [
        "リハビリへの意欲が低下している。",
        "メンタルの状態は良好だ。",
        "リハビリへの覇気が感じられない。",
        "食事の摂取量は良好だ。",
        "バイタルは安定している。"
    ]

    # ウォームアップ
    print("\n[Warmup]...")
    if quantized_ai.model: quantized_ai.analyze("テスト")

    results = []
    print("\n=== Running Speed Benchmark (CPU) ===")

    for text in test_cases:
        # A. Rule V2.2
        start = time.perf_counter()
        _ = rule_v2_2.analyze(text)
        rule_time = (time.perf_counter() - start) * 1000

        # B. Normal mDeBERTa
        start = time.perf_counter()
        with torch.no_grad():
            inputs = normal_tokenizer(text, "仮説", truncation=True, return_tensors="pt")
            _ = normal_model(**inputs)
        normal_time = (time.perf_counter() - start) * 1000

        # C. Quantized BERT
        start = time.perf_counter()
        _ = quantized_ai.analyze(text)
        quant_time = (time.perf_counter() - start) * 1000

        results.append({
            "Text": text[:10] + "..",
            "Rule V2.2 (ms)": round(rule_time, 2),
            "Normal AI (ms)": round(normal_time, 2),
            "Quantized AI (ms)": round(quant_time, 2)
        })

    df = pd.DataFrame(results)
    
    print("\n=== Processing Time Comparison ===")
    print(df.to_markdown(index=False))

    # 平均速度と倍率
    avg_rule = df["Rule V2.2 (ms)"].mean()
    avg_quant = df["Quantized AI (ms)"].mean()
    
    print(f"\n[Conclusion]")
    print(f"Rule V2.2 Average: {avg_rule:.2f} ms")
    print(f"Quantized AI Avg : {avg_quant:.2f} ms")
    if avg_rule > 0:
        print(f"-> Rule V2.2 is {avg_quant / avg_rule:.1f}x faster than Quantized AI.")

if __name__ == "__main__":
    main()