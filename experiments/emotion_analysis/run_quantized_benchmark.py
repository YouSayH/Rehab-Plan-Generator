import time
import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 既存のルールベース読み込み
from methods.aspect_rule_v2_2 import AspectRuleAnalyzerV2_2

class QuantizedNLIAnalyzer:
    def __init__(self, model_name="MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"):
        print(f"[Quantized NLI] Loading {model_name}...")
        self.device = "cpu" # 量子化はCPU専用の最適化技術です
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            # 1. 通常のモデルをロード
            base_model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self.device)
            
            # 2. 【魔法の1行】 動的量子化を適用 (Linear層をint8化)
            print("[Quantized NLI] Applying Dynamic Quantization (float32 -> int8)...")
            self.model = torch.quantization.quantize_dynamic(
                base_model, 
                {torch.nn.Linear},  # 量子化するレイヤー
                dtype=torch.qint8   # 8ビット整数に圧縮
            )
            
            self.hypothesis = "患者はリハビリに対して意欲的で、状態は良好である。"
            print("[Quantized NLI] Ready.")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    def analyze(self, text: str):
        if not self.model: return {"score": 0}
        
        # 推論実行
        inputs = self.tokenizer(text, self.hypothesis, truncation=True, return_tensors="pt").to(self.device)
        with torch.no_grad():
            output = self.model(inputs["input_ids"])
        
        probs = torch.softmax(output["logits"][0], -1).tolist()
        score = probs[0] - probs[2] # Entailment - Contradiction
        
        label = "NEUTRAL"
        if score > 0.2: label = "POSITIVE"
        if score < -0.2: label = "NEGATIVE"

        return {"score": round(score, 3), "label": label, "details": probs}

def main():
    # 1. モデル準備
    print("--- Initializing ---")
    rule_v2_2 = AspectRuleAnalyzerV2_2()
    quantized_nli = QuantizedNLIAnalyzer()
    
    # 比較用：通常の重いモデル（オンメモリで比較するため再ロード）
    print("[Normal NLI] Loading standard model for comparison...")
    normal_tokenizer = AutoTokenizer.from_pretrained("MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7")
    normal_model = AutoModelForSequenceClassification.from_pretrained("MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7").to("cpu")

    # テストケース
    test_cases = [
        "リハビリへの意欲が低下している。",
        "メンタルの状態は良好だ。",
        "リハビリへの覇気が感じられない。",
        "食事の摂取量は良好だ。",
        "訓練に対する不満はない。"
    ]

    # ウォームアップ
    quantized_nli.analyze("テスト")

    results = []
    print("\n--- Running Benchmark (CPU) ---")

    for text in test_cases:
        # 1. Rule V2.2
        start = time.perf_counter()
        rule_res = rule_v2_2.analyze(text)
        rule_time = (time.perf_counter() - start) * 1000

        # 2. Normal NLI (比較対象)
        start = time.perf_counter()
        with torch.no_grad():
            inputs = normal_tokenizer(text, "患者はリハビリに対して意欲的で、状態は良好である。", truncation=True, return_tensors="pt")
            _ = normal_model(**inputs)
        normal_time = (time.perf_counter() - start) * 1000

        # 3. Quantized NLI (主役)
        start = time.perf_counter()
        quant_res = quantized_nli.analyze(text)
        quant_time = (time.perf_counter() - start) * 1000

        results.append({
            "Text": text[:10] + "..",
            "Rule V2.2 (ms)": round(rule_time, 2),
            "Normal AI (ms)": round(normal_time, 2),
            "Quantized AI (ms)": round(quant_time, 2),
            "Q-AI Score": quant_res["score"],
            "Q-AI Label": quant_res["label"]
        })

    df = pd.DataFrame(results)
    
    print("\n=== Speed Comparison ===")
    print(df[["Text", "Rule V2.2 (ms)", "Normal AI (ms)", "Quantized AI (ms)"]].to_markdown(index=False))

    print("\n=== Quantized AI Accuracy Check ===")
    print(df[["Text", "Q-AI Score", "Q-AI Label"]].to_markdown(index=False))

    # 平均速度の算出
    avg_normal = df["Normal AI (ms)"].mean()
    avg_quant = df["Quantized AI (ms)"].mean()
    speedup = avg_normal / avg_quant if avg_quant > 0 else 0
    
    print(f"\nResult: Quantized AI is {speedup:.1f}x faster than Normal AI.")

if __name__ == "__main__":
    main()