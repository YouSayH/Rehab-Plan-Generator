import sys
import os
import inspect
from pydantic import BaseModel, ConfigDict, ValidationError

# ----------------------------------------------------------------
# パス設定: backendディレクトリをインポートパスに追加
# ----------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__)) # .../backend/tools
backend_dir = os.path.dirname(current_dir)             # .../backend
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

try:
    # アプリケーションのスキーマ定義とシーダーデータをインポート
    from app.schemas import extraction_schemas
    from app.schemas.extraction_schemas import PatientExtractionSchema
    from tools.seeder import DUMMY_PATIENTS
except ImportError as e:
    print("Error: モジュールのインポートに失敗しました。")
    print("実行ディレクトリが 'backend' であるか確認してください。(例: python tools/check_seeder_schema.py)")
    print(f"詳細: {e}")
    sys.exit(1)

def enable_strict_validation():
    """
    extraction_schemas モジュール内の全てのPydanticモデルに対して
    extra='forbid' (未定義フィールドを禁止) を設定し、モデルを再構築する。
    これにより、Typoなどで存在しないキーが含まれている場合にエラーが発生するようになる。
    """
    print("スキーマの厳格モード(extra='forbid')を有効化しています...")
    
    # モジュール内で定義されている Pydantic モデルクラスを収集
    target_models = []
    for name, obj in inspect.getmembers(extraction_schemas):
        if inspect.isclass(obj) and issubclass(obj, BaseModel):
            # 基底クラス自体は除外
            if obj is BaseModel:
                continue
            # このモジュールで定義されたクラスのみ対象（外部ライブラリ等は除外）
            if obj.__module__ == extraction_schemas.__name__:
                target_models.append(obj)
    
    # 設定を変更して再構築 (Pydantic V2対応)
    for model in target_models:
        model.model_config = ConfigDict(extra='forbid')
        model.model_rebuild(force=True)

def check_seeder_data():
    print(f"シーダーデータ ({len(DUMMY_PATIENTS)}件) のスキーマ整合性をチェックします...\n")
    
    # 厳格モード有効化
    enable_strict_validation()
    
    error_count = 0
    
    for patient in DUMMY_PATIENTS:
        hash_id = patient.get("hash_id", "Unknown ID")
        extraction_data = patient.get("extraction_data")
        
        if not extraction_data:
            print(f"[SKIP] {hash_id}: 'extraction_data' キーが見つかりません。")
            continue
            
        try:
            # バリデーション実行
            PatientExtractionSchema(**extraction_data)
            print(f"[OK] {hash_id}: Valid")
            
        except ValidationError as e:
            error_count += 1
            print(f"[ERROR] {hash_id}: スキーマ違反が見つかりました")
            
            for err in e.errors():
                # エラー箇所と理由を表示
                loc = " -> ".join(str(l) for l in err['loc'])
                msg = err['msg']
                
                print(f"  - 項目: {loc}")
                print(f"    理由: {msg}")
                # "Extra inputs not permitted" の場合は未定義のフィールドがあるということ
                if err['type'] == 'extra_forbidden':
                    print(f"    ⚠️  存在しないフィールド '{loc.split(' -> ')[-1]}' が含まれています (Typoの可能性があります)")
            print("-" * 40)
            
        except Exception as e:
            error_count += 1
            print(f"[ERROR] {hash_id}: 予期せぬエラー: {e}")

    print("\n" + "="*30)
    if error_count == 0:
        print("✅ 全てのデータがスキーマ定義と一致しています。")
        sys.exit(0)
    else:
        print(f"❌ {error_count} 件のデータでエラーが見つかりました。修正してください。")
        sys.exit(1)

if __name__ == "__main__":
    check_seeder_data()