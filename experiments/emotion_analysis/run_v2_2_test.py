import pandas as pd
from methods.aspect_rule_v2_2 import AspectRuleAnalyzerV2_2

def main():
    analyzer = AspectRuleAnalyzerV2_2()
    
    # 難易度の高いテストケース
    test_cases = [
        # 1. 中継地点 (Passthrough) テスト
        "メンタルの状態は良好だ。",         # [メンタル] -> [状態] -> [良好]
        "練習の様子を見ていると意欲的だ。", # [練習] -> [様子] -> ... -> [意欲的]

        # 2. 兄弟否定 (Sibling Negation) テスト
        "リハビリへの覇気が感じられない。", # [覇気] -> [感じ] <- [ない] (覇気はDirect, ないはSibling)
        "笑顔は見られない。",               # [笑顔] -> [見] <- [ない]
        
        # 3. 誤検知回避テスト
        "食事の摂取量は良好だ。",           # 食事はターゲット外
        "睡眠の状態は悪い。",               # 睡眠はターゲット外
        
        # 4. 複雑な否定
        "訓練に対する不満はない。",         # [不満](-1) + [ない](Neg) -> +1
    ]

    results = []
    print("\n=== Running V2.2 Verification ===")
    
    for text in test_cases:
        res = analyzer.analyze(text)
        results.append({
            "Text": text,
            "Score": res["score"],
            "Label": res["label"],
            "Details": str(res["details"])
        })

    df = pd.DataFrame(results)
    print(df.to_markdown(index=False))

if __name__ == "__main__":
    main()