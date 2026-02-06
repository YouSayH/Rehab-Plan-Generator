import pandas as pd
from methods.aspect_rule_v2 import AspectRuleAnalyzerV2
from methods.aspect_rule_v3 import AspectRuleAnalyzerV3

def main():
    print("=== Initializing Comparison ===")
    v2 = AspectRuleAnalyzerV2() # 辞書のみ
    v3 = AspectRuleAnalyzerV3() # 辞書 + ベクトル
    
    analyzers = [v2, v3]

    test_cases = [
        # 1. 基礎（両方できるべき）
        "リハビリへの意欲が低下している。",
        
        # 2. V3の強み（未知語への対応）
        "リハビリへの覇気が感じられない。", # 「覇気」はV2辞書にない
        "メンタルの状態は良好だ。",         # 「メンタル」はV2辞書にない
        
        # 3. V3の弱点チェック（誤検知しないか？）
        "食事の摂取量は良好だ。",           # 「食事」と「意欲」は似て非なるもの
        "睡眠の状態は悪い。",               # 「睡眠」と「意欲」
        "バイタルは安定している。"          # 「バイタル」
    ]

    results = []
    print("\n=== Running V2 vs V3 ===")
    
    for text in test_cases:
        for analyzer in analyzers:
            res = analyzer.analyze(text)
            results.append({
                "Text": text,
                "Method": res["method"],
                "Score": res["score"],
                "Details": str(res["details"])
            })

    df = pd.DataFrame(results)
    
    # ピボットテーブルで見やすく比較
    print("\n=== Comparison Matrix (Scores) ===")
    pivot = df.pivot(index="Text", columns="Method", values="Score")
    print(pivot.to_markdown())

    print("\n=== Detection Details (Why?) ===")
    # 詳細な検知理由を表示
    for text in test_cases:
        print(f"\nText: {text}")
        v2_res = df[(df["Text"]==text) & (df["Method"].str.contains("V2"))].iloc[0]
        v3_res = df[(df["Text"]==text) & (df["Method"].str.contains("V3"))].iloc[0]
        print(f"  V2: {v2_res['Score']} -> {v2_res['Details']}")
        print(f"  V3: {v3_res['Score']} -> {v3_res['Details']}")

if __name__ == "__main__":
    main()