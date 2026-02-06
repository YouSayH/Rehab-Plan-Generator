import pandas as pd
from methods.aspect_rule_v2_1 import AspectRuleAnalyzerV2_1

def main():
    analyzer = AspectRuleAnalyzerV2_1()
    
    test_cases = [
        "メンタルの状態は良好だ。",         # [メンタル] -> [状態] -> [良好] (中継ロジックが必要)
        "リハビリへの覇気が感じられない。", # [覇気] -> [感じ] -> [ない] (中継ロジックが必要)
        "食事の摂取量は良好だ。",           # [食事] -> [摂取量] (食事はターゲット外なので無視すべき)
        "バイタルは安定している。",         # 無視すべき
    ]

    results = []
    print("\n=== Running V2.1 Test ===")
    for text in test_cases:
        res = analyzer.analyze(text)
        results.append({
            "Text": text,
            "Score": res["score"],
            "Label": res["label"],
            "Details": str(res["details"])
        })

    print(pd.DataFrame(results).to_markdown())

if __name__ == "__main__":
    main()