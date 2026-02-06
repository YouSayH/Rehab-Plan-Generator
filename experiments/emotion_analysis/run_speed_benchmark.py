import time
import pandas as pd
import torch
from methods.aspect_rule_v2 import AspectRuleAnalyzerV2
from methods.aspect_rule_v2_1 import AspectRuleAnalyzerV2_1
from methods.aspect_rule_v3 import AspectRuleAnalyzerV3
from methods.nli_score import NLIAnalyzer

def main():
    print("=== Environment Check ===")
    print(f"PyTorch Version: {torch.__version__}")
    print(f"CUDA Available : {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU Device     : {torch.cuda.get_device_name(0)}")
    else:
        print("Running on CPU mode (NLI will be slow)")

    print("\n=== Initializing Models ===")
    analyzers = [
        AspectRuleAnalyzerV2(),
        AspectRuleAnalyzerV2_1(),
        AspectRuleAnalyzerV3(),
        NLIAnalyzer()
    ]

    # 難易度の高いテストケース
    test_cases = [
        "リハビリへの意欲が低下している。",         # Basic
        "メンタルの状態は良好だ。",                 # V2.1 Target (Passthrough)
        "リハビリへの覇気が感じられない。",         # V2.1 Target (Unknown word + Passthrough)
        "食事の摂取量は良好だ。",                   # Trap (Should be Neutral)
        "バイタルは安定している。",                 # Trap (Should be Neutral)
    ]

    # ウォームアップ (初回ロード遅延の除外)
    print("\n[Warmup] Running dummy inference...")
    for analyzer in analyzers:
        try:
            analyzer.analyze("テスト")
        except: pass

    results = []
    print("\n=== Running Benchmark ===")
    
    for text in test_cases:
        for analyzer in analyzers:
            try:
                # 計測開始
                start_time = time.perf_counter()
                
                res = analyzer.analyze(text)
                
                # 計測終了
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000

                results.append({
                    "Text": text[:10] + "..",
                    "Method": res.get("method", type(analyzer).__name__),
                    "Score": res.get("score", 0),
                    "Time(ms)": round(duration_ms, 2),
                    "Details": str(res.get("details", ""))[:20] + ".."
                })
            except Exception as e:
                print(f"Error in {analyzer}: {e}")

    df = pd.DataFrame(results)
    
    # 1. 速度比較テーブル
    print("\n=== Processing Time Comparison (Average) ===")
    avg_time = df.groupby("Method")["Time(ms)"].mean().sort_values()
    print(avg_time.to_markdown())

    # 2. スコア比較テーブル (精度)
    print("\n=== Score Accuracy Comparison ===")
    pivot = df.pivot(index="Text", columns="Method", values="Score")
    print(pivot.to_markdown())

    # 3. 総合結果
    print("\n=== Detailed Log ===")
    print(df.to_markdown(index=False))

if __name__ == "__main__":
    main()
