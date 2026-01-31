import os
import json
import pytest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel, Field

# テスト対象のクラスをインポート
# ※ 実際のディレクトリ構成に合わせてパス調整が必要な場合があります
from app.adapters.llm.gemini_client import GeminiClient

# ----------------------------------------------------------------
# テスト用データの定義
# ----------------------------------------------------------------
class SampleSchema(BaseModel):
    name: str = Field(description="名前")
    age: int = Field(description="年齢")

# ----------------------------------------------------------------
# Fixture (前準備)
# ----------------------------------------------------------------
@pytest.fixture
def mock_genai_client():
    """
    google.genai.Client のモックを作成します。
    __init__ でインスタンス化されるため、パッチを当てる必要があります。
    """
    with patch("app.adapters.llm.gemini_client.genai.Client") as mock_class:
        # Client() が返すインスタンスのモック
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def client(mock_genai_client):
    """
    環境変数をセットした状態で GeminiClient を初期化します。
    """
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key", "GEMINI_MODEL": "gemini-test"}):
        return GeminiClient()

# ----------------------------------------------------------------
# テストケース
# ----------------------------------------------------------------

@pytest.mark.asyncio
async def test_init(client):
    """初期化処理のテスト: 環境変数が正しく読み込まれているか"""
    assert client.model_name == "gemini-test"
    # GenAIクライアントがAPIキー付きで初期化されたか確認
    # (patchしたクラスが呼ばれたか)
    from app.adapters.llm.gemini_client import genai
    genai.Client.assert_called_with(api_key="fake_key")


@pytest.mark.asyncio
async def test_generate_text_success(client, mock_genai_client):
    """generate_text: 正常系"""
    # モックの振る舞い定義
    mock_response = MagicMock()
    mock_response.text = "Hello, World!"
    mock_genai_client.models.generate_content.return_value = mock_response

    # 実行
    prompt = "Say hello"
    result = await client.generate_text(prompt)

    # 検証
    assert result == "Hello, World!"
    
    # SDKのメソッドが正しい引数で呼ばれたか検証
    # asyncio.to_thread 経由でも call_args は記録されます
    args, kwargs = mock_genai_client.models.generate_content.call_args
    assert kwargs["model"] == "gemini-test"
    assert kwargs["contents"] == prompt
    # configでtemperature=0.7がセットされているか
    assert kwargs["config"].temperature == 0.7


@pytest.mark.asyncio
async def test_generate_text_failure(client, mock_genai_client):
    """generate_text: SDKがエラーを吐いた場合"""
    # エラーを送出するように設定
    mock_genai_client.models.generate_content.side_effect = Exception("API Error")

    with pytest.raises(Exception) as excinfo:
        await client.generate_text("test")
    
    assert "API Error" in str(excinfo.value)


@pytest.mark.asyncio
async def test_generate_json_success(client, mock_genai_client):
    """generate_json: 正常系"""
    # 期待するJSONレスポンス
    expected_data = {"name": "Taro", "age": 30}
    
    mock_response = MagicMock()
    mock_response.text = json.dumps(expected_data)
    mock_genai_client.models.generate_content.return_value = mock_response

    # 実行
    prompt = "Extract info"
    result = await client.generate_json(prompt, SampleSchema)

    # 検証
    assert result == expected_data
    
    # 呼び出し引数の検証 (Structured Output設定)
    args, kwargs = mock_genai_client.models.generate_content.call_args
    config = kwargs["config"]
    
    assert config.response_mime_type == "application/json"
    # スキーマが正しくセットされているか (簡易チェック)
    assert "properties" in config.response_json_schema


@pytest.mark.asyncio
async def test_generate_json_decode_error(client, mock_genai_client):
    """generate_json: モデルが壊れたJSONを返した場合"""
    mock_response = MagicMock()
    mock_response.text = "This is not JSON"
    mock_genai_client.models.generate_content.return_value = mock_response

    # JSONDecodeErrorが発生することを確認
    with pytest.raises(json.JSONDecodeError):
        await client.generate_json("test", SampleSchema)