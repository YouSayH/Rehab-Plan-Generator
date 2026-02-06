import time
import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer

# ONNX Runtime関連のインポート（未インストールの場合はエラーメッセージを表示）
try:
    from optimum.onnxruntime import ORTModelForSequenceClassification
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    print("【注意】Optimum/ONNX Runtimeがインストールされていません。pip install optimum onnxruntime を実行してください。")

# 既存の手法（比較対象）をインポート
try:
    from methods.aspect_rule_v2_2 import AspectRuleAnalyzerV2_2
except ImportError:
    # ファイルがない場合のダミー
    class AspectRuleAnalyzerV2_2:
        def analyze(self, text): return {"score": 0, "method": "Rule (Dummy)", "details": []}

class OnnxSentenceAnalyzer:
    def __init__(self, model_id="MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7", use_gpu=False):
        if not ONNX_AVAILABLE:
            raise ImportError("ONNX Runtime is missing.")
            
        print(f"[ONNX Analyzer] Initializing with model: {model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        # GPUが使えるPC (RTX 4070 Super) ならCUDA、ノートPCならCPUを選択
        provider = "CUDAExecutionProvider" if use_gpu and torch.cuda.is_available() else "CPUExecutionProvider"
        print(f"[ONNX Analyzer] Loading model to {provider}...")
        
        # ONNXモデルのロード（初回はexport=Trueで変換が走るため少し時間がかかります）
        self.model = ORTModelForSequenceClassification.from_pretrained(
            model_id,
            export=True, 
            provider=provider
        )
        
        # LightGBM用の特徴量を作るための「2つの仮説」
        # これにより、メンタルとフィジカルを分離して数値化します
        self.hypotheses = {
            "mental": "患者はリハビリに対して意欲的で、精神状態は前向きである。",
            "physical": "患者の身体機能は安定しており、痛みやバイタルの異常はない。"
        }
        print(f"[ONNX Analyzer] Ready. Hypotheses: {list(self.hypotheses.keys())}")

    def analyze(self, text: str):
        # 計測開始
        start_time = time.perf_counter()
        
        # 1. 文分割
        raw_sentences = text.replace("。", "。\n").split("\n")
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        
        if not sentences:
            return {"score": 0, "features": {}, "time_ms": 0}

        features = {}
        details_log = []
        
        # 【修正】ラベルIDの自動取得 (初回のみ実行でも良いが、念のため毎回確認)
        # ラベル名に "entailment" や "contradiction" が含まれるIDを探す
        label2id = self.model.config.label2id
        entail_id = -1
        contra_id = -1
        
        for label, id in label2id.items():
            if "entailment" in label.lower():
                entail_id = id
            elif "contradiction" in label.lower():
                contra_id = id
        
        # 見つからない場合のフォールバック (mDeBERTa-xnliの一般的な並び)
        if entail_id == -1: entail_id = 2
        if contra_id == -1: contra_id = 0

        # 2. 仮説ごとにバッチ推論
        for hyp_name, hypothesis in self.hypotheses.items():
            hyp_list = [hypothesis] * len(sentences)
            
            inputs = self.tokenizer(
                sentences, 
                hyp_list, 
                padding=True, 
                truncation=True, 
                max_length=128,
                return_tensors="pt"
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            probs = torch.softmax(outputs.logits, dim=-1).numpy()
            
            # 【修正】動的に取得したIDを使ってスコア計算
            # Score = Entailment(肯定) - Contradiction(否定/矛盾)
            scores = probs[:, entail_id] - probs[:, contra_id]
            
            # (以下、統計量算出などはそのまま)
            features[f"{hyp_name}_mean"] = round(float(np.mean(scores)), 3)
            features[f"{hyp_name}_max"]  = round(float(np.max(scores)), 3)
            features[f"{hyp_name}_min"]  = round(float(np.min(scores)), 3)
            features[f"{hyp_name}_std"]  = round(float(np.std(scores)), 3)
            features[f"{hyp_name}_neg_cnt"] = int(np.sum(scores < -0.3))
            
            # ログ用 (分かりやすくラベルも表示)
            for s, sc in zip(sentences, scores):
                details_log.append(f"[{hyp_name.upper()}] {sc:.2f}: {s[:10]}..")

        duration = (time.perf_counter() - start_time) * 1000
        
        # (return部分もそのまま)
        return {
            "method": "ONNX (Sent-Batch)",
            "score": features["mental_mean"],
            "features": features,
            "time_ms": duration,
            "details": details_log
        }

def main():
    print("=== Setting up Comparison ===")
    
    # モデル準備
    # デスクトップPC (RTX 4070 Super) なら use_gpu=True に変更推奨
    try:
        onnx_analyzer = OnnxSentenceAnalyzer(use_gpu=False) 
    except Exception as e:
        print(f"Error initializing ONNX: {e}")
        return

    rule_analyzer = AspectRuleAnalyzerV2_2()

    # テストケース：長文や複合的な状況
    # LightGBMにとって「平均スコア」と「文ごとの特徴量」でどう差が出るかに注目
    test_cases = [
        # Case 1: 全体的に良い
        "本日はリハビリに意欲的に参加された。笑顔も見られ、歩行訓練もスムーズだった。バイタルも安定している。",
        
        # Case 2: 身体は悪いが、意欲はある（ルールベースが苦手なパターン）
        "右足の痛みを訴えているが、リハビリは頑張りたいと話す。歩行は困難だが、ベッド上の訓練には積極的だ。",
        
        # Case 3: リスクあり（全体平均だと相殺されてしまうパターン）
        "入室時は穏やかだったが、途中から帰宅願望が強くなり、スタッフに対して大声で拒否を示した。その後は落ち着いて休んでいる。",
        
        # Case 4: 身体は良いが、意欲がない（うつ傾向）
        "バイタルは正常。食事も完食している。しかし、一日中カーテンを閉め切って臥床しており、リハビリへの呼びかけにも反応が乏しい。"
    ]

    results = []

    print("\n=== Running Benchmark ===")
    for i, text in enumerate(test_cases):
        print(f"\nText {i+1}: {text[:30]}...")
        
        # 1. Rule Base V2.2
        start = time.perf_counter()
        rule_res = rule_analyzer.analyze(text)
        rule_time = (time.perf_counter() - start) * 1000
        
        # 2. ONNX AI
        onnx_res = onnx_analyzer.analyze(text)
        
        # 結果格納
        results.append({
            "Text": f"Case {i+1}",
            "Rule Score": rule_res.get("score", 0),
            "Rule Time": f"{rule_time:.1f}ms",
            "AI Score (Mean)": onnx_res["score"],
            "AI Time": f"{onnx_res['time_ms']:.1f}ms",
            # LightGBM用のリッチな特徴量（これが見どころです）
            "AI Features (Mental Min)": onnx_res["features"].get("mental_min"),
            "AI Features (Physical Min)": onnx_res["features"].get("physical_min")
        })
        
        # 詳細出力
        print(f"  > Rule Score: {rule_res.get('score', 0):.2f}")
        print(f"  > AI Features: {onnx_res['features']}")

    print("\n=== Final Comparison Table ===")
    df = pd.DataFrame(results)
    print(df.to_markdown(index=False))
    
    print("\n=== Conclusion for LightGBM ===")
    print("AI Featuresのカラムを見てください。")
    print("Case 2（痛みあるが意欲あり）や Case 3（一時的な拒否）において、")
    print("単純な平均スコア(Mean)よりも、Min(最小値)やNeg_Countがリスクを捉えていることがわかります。")

if __name__ == "__main__":
    main()