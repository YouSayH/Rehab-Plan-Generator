# backend/tests/unit/schemas/test_schema_coverage.py

import pytest
from app.schemas.extraction_schemas import PatientExtractionSchema
# テスト用ディレクトリに配置した旧スキーマをインポート
from .legacy_schemas import PatientMasterSchema

class TestSchemaCoverage:
    """
    新スキーマ(PatientExtractionSchema)が、
    旧スキーマ(legacy_schemas.PatientMasterSchema)の全項目を網羅しているか検証する回帰テスト。
    """

    def test_perfect_match_legacy_keys(self):
        # 1. 旧スキーマの全フィールド名を取得
        legacy_keys = set(PatientMasterSchema.model_fields.keys())

        # 2. 新スキーマをダミーインスタンス化して変換後のキーを取得
        # 全フィールドがOptionalなので引数なしで生成可能
        dummy_instance = PatientExtractionSchema(
            basic={}, medical={}, function={}, basic_movement={}, 
            adl={}, nutrition={}, social={}, goals={}, signature={}
        )
        
        # 変換実行
        exported_data = dummy_instance.export_to_mapping_format()
        new_keys = set(exported_data.keys())

        # 3. 比較検証
        missing_keys = legacy_keys - new_keys
        extra_keys = new_keys - legacy_keys

        # 4. アサーション (判定)
        
        # 欠落キーがあってはならない
        assert not missing_keys, f"Missing {len(missing_keys)} keys: {sorted(missing_keys)}"
        
        # 過剰キーがあってはならない (完全一致を目指す場合)
        # もし将来的に新機能でキーを増やす場合は、ここを緩和するか、legacy_schemasを更新する必要があります
        assert not extra_keys, f"Extra {len(extra_keys)} keys found: {sorted(extra_keys)}"