# check_error.py
import sys
print(f"Python: {sys.version}")

print("--- Importing onnxruntime ---")
try:
    import onnxruntime
    print(f"Success: onnxruntime {onnxruntime.__version__}")
except ImportError as e:
    print(f"FAILED onnxruntime: {e}")
except Exception as e:
    print(f"CRITICAL onnxruntime: {e}")

print("\n--- Importing optimum.onnxruntime ---")
try:
    # ここが本丸です。詳細なトレースバックを表示させます
    from optimum.onnxruntime import ORTModelForSequenceClassification
    print("Success: Optimum loaded!")
except Exception as e:
    import traceback
    traceback.print_exc()