"""
File: backend/tools/check_keys.py

Summary:
フロントエンドとバックエンド間のデータキーの整合性を検証するクロスチェックツール。
バックエンドの定数（`constants.py` の `PATIENT_FIELD_LABELS`）と、フロントエンドの型定義（`frontend/src/api/types.ts` の `CELL_MAPPING`）を読み込み、フロントエンドで利用されているキーがバックエンド側に存在するかを突き合わせます。スプレッドシートへの出力エラーを未然に防ぐ役割を持ちます。

Tags: Tool, Utility, Validation, Consistency, Frontend-Backend
"""

import sys
import os
import re
from pathlib import Path

# --- パス設定 ---
# このファイルの親ディレクトリの親ディレクトリ(=backend)をパスに追加して
# 'app' モジュールをインポートできるようにする
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
PROJECT_ROOT = BACKEND_ROOT.parent

sys.path.append(str(BACKEND_ROOT))

# 依存関係なしで定数ファイルのみをインポート
# ※ constants.py が外部ライブラリをimportしているとここでエラーになるが、
#    現状のコードでは標準型のみなので問題なし。
try:
    from app.core.constants import PATIENT_FIELD_LABELS
except ImportError as e:
    print(f"Error importing backend constants: {e}")
    print("Ensure you are running this script with a Python environment that can see the 'app' package.")
    sys.exit(1)

def parse_frontend_keys(frontend_path: Path) -> set:
    """
    types.ts をテキストとして読み込み、CELL_MAPPING 内のキーを抽出する
    """
    if not frontend_path.exists():
        print(f"[ERROR] Frontend file not found at: {frontend_path}")
        print("Please check the path or run this script from the project root.")
        return set()

    with open(frontend_path, "r", encoding="utf-8") as f:
        content = f.read()

    keys = set()
    is_in_mapping = False
    
    # 簡易的な構文解析
    for line in content.splitlines():
        # export const CELL_MAPPING = { ... } の開始を探す
        if "export const CELL_MAPPING" in line:
            is_in_mapping = True
            continue
        
        # 定義の終了 }; を探す
        if is_in_mapping and "};" in line:
            break
        
        # キーの抽出: "  key_name: { ... }," のパターン
        if is_in_mapping:
            # 行頭の空白 + 英数字/アンダースコア + コロン
            match = re.search(r'^\s*([a-zA-Z0-9_]+):', line)
            if match:
                keys.add(match.group(1))
    
    return keys

def main():
    # ファイルパスの特定
    frontend_types_path = PROJECT_ROOT / "frontend" / "src" / "api" / "types.ts"

    print("🔍 Checking key consistency...")
    print(f"   Backend Path:  {BACKEND_ROOT}")
    print(f"   Frontend Path: {frontend_types_path}")

    # 1. Backendキーの取得
    backend_keys = set(PATIENT_FIELD_LABELS.keys())
    
    # 2. Frontendキーの抽出
    frontend_keys = parse_frontend_keys(frontend_types_path)
    
    if not frontend_keys:
        print("⚠️  No keys found in Frontend or file unreadable.")
        sys.exit(1)

    print(f"   Backend Keys:  {len(backend_keys)}")
    print(f"   Frontend Keys: {len(frontend_keys)}")

    # 3. 比較: FrontendにあるがBackendにないキー (エラー対象)
    missing_in_backend = frontend_keys - backend_keys
    
    # 4. 比較: BackendにあるがFrontendで使われていないキー (情報のみ)
    unused_in_frontend = backend_keys - frontend_keys

    # --- 結果出力 ---
    if missing_in_backend:
        print("\n❌ [FAIL] Key Mismatch Detected!")
        print("The following keys are used in Frontend (types.ts) but NOT defined in Backend (constants.py):")
        print("This will cause Univer to fail displaying generated data.")
        print("-" * 60)
        for k in sorted(missing_in_backend):
            print(f" - {k}")
        print("-" * 60)
        print("👉 Action: Rename these keys in 'frontend/src/api/types.ts' to match Backend definitions.")
        sys.exit(1) # 異常終了
    else:
        print("\n✅ [PASS] All Frontend keys are valid and match Backend definitions.")
        
        if unused_in_frontend:
            print(f"   (Info: {len(unused_in_frontend)} keys from Backend are not yet mapped in Frontend.)")
        
        sys.exit(0) # 正常終了

if __name__ == "__main__":
    main()