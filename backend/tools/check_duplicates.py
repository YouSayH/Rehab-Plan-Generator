import sys
import os
import ast
from pathlib import Path

# パス設定
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
CONSTANTS_PATH = BACKEND_ROOT / "app" / "core" / "constants.py"

def check_dict_duplicates(file_path):
    print(f"🔍 Checking for duplicates in: {file_path}")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"❌ Syntax Error in file: {e}")
        sys.exit(1)

    duplicates_found = False

    # ASTを巡回して辞書定義を探す
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # 変数名を取得 (PATIENT_FIELD_LABELS かどうか)
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PATIENT_FIELD_LABELS":
                    if isinstance(node.value, ast.Dict):
                        seen_keys = set()
                        for key_node in node.value.keys:
                            if isinstance(key_node, ast.Constant): # Python 3.8+
                                key = key_node.value
                            elif isinstance(key_node, ast.Str): # Python < 3.8
                                key = key_node.s
                            else:
                                continue # 文字列以外のキーはスキップ
                            
                            if key in seen_keys:
                                print(f"⚠️  Duplicate key found: '{key}' (Line {key_node.lineno})")
                                duplicates_found = True
                            else:
                                seen_keys.add(key)
    
    if duplicates_found:
        print("\n❌ [FAIL] Duplicates detected! The later definition will overwrite the earlier one.")
        print("👉 Action: Remove duplicate lines in 'backend/app/core/constants.py'.")
        sys.exit(1)
    else:
        print("\n✅ [PASS] No duplicate keys found in PATIENT_FIELD_LABELS.")

if __name__ == "__main__":
    check_dict_duplicates(CONSTANTS_PATH)