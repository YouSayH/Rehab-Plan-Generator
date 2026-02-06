import pandas as pd
from methods.sentiment_bert import BertSentimentAnalyzer
from methods.behavior_rule import RuleBasedAnalyzer
from methods.nli_score import NLIAnalyzer
from methods.slm_ollama import OllamaAnalyzer
from methods.aspect_rule import AspectRuleAnalyzer
from methods.aspect_rule_v2 import AspectRuleAnalyzerV2
from methods.aspect_vector import VectorAspectAnalyzer

def main():
    print("=== Initializing All Analyzers ===")
    analyzers = [
        BertSentimentAnalyzer(),    # 一般的な感情分析
        RuleBasedAnalyzer(),        # 単純辞書
        NLIAnalyzer(),             # 含意関係
        AspectRuleAnalyzer(),       # 係り受けアスペクト
        AspectRuleAnalyzerV2(),
        VectorAspectAnalyzer(),     # ベクトルアスペクト (自動拡張)
        OllamaAnalyzer()          # 必要に応じてコメントアウト解除
    ]

    test_cases = [
        "笑顔でリハビリに参加できている。",                 # 明確なPositive
        "リハビリへの意欲が低下している。",                 # 明確なNegative
        "右足の痛みが強く、歩行が困難である。",             # 身体的Negative (精神はNeutralであるべき)
        "本日はリハビリを拒否された。",                     # 行動的Negative
        "訓練に対する不満はない。",                         # 否定の否定 -> Positive
        "食事の摂取量は良好である。"                        # ターゲット外 -> Neutral
    ]

    results = []
    print("\n=== Running Comparison ===")
    
    for text in test_cases:
        print(f"Analyzing: {text[:15]}...")
        for analyzer in analyzers:
            try:
                res = analyzer.analyze(text)
                results.append({
                    "Text": text,
                    "Method": res.get("method", "Unknown"),
                    "Score": res.get("score", 0),
                    "Label": res.get("label", "Error"),
                    "Details": str(res.get("details", ""))[:30]
                })
            except Exception as e:
                print(f"Error: {e}")

    if results:
        df = pd.DataFrame(results)
        # スコア比較用のピボットテーブル
        print("\n=== Score Comparison Matrix ===")
        print(df.pivot(index="Text", columns="Method", values="Score").to_markdown())
        
        # 詳細保存
        df.to_csv("comparison_results.csv", index=False)
        print("\nSaved detailed results to comparison_results.csv")

if __name__ == "__main__":
    main()
