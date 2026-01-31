import os
import json
import pytest
from unittest.mock import MagicMock, patch, ANY
from pydantic import BaseModel, Field

# テスト対象クラス
from app.adapters.llm.ollama_client import OllamaClient

# ----------------------------------------------------------------
# テスト用データの定義
# ----------------------------------------------------------------
class SampleSchema(BaseModel):
    summary: str = Field(description="要約")
    score: int = Field(description="スコア")

# ----------------------------------------------------------------
# Helper: モックレスポンス生成器
# ----------------------------------------------------------------
def create_mock_chunk(content=None, thinking=None):
    """Ollamaのレスポンスチャンクを模倣するオブジェクトを作成"""
    chunk = MagicMock()
    # message属性とその中身を設定
    message = MagicMock()
    # 属性としてアクセスできるように設定 (getattr対応)
    message.content = content
    message.thinking = thinking
    chunk.message = message
    return chunk

# ----------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------
@pytest.fixture
def mock_ollama_lib():
    """
    ollama.Client クラス自体をモック化して返します。
    インスタンスへのアクセスは mock_class.return_value を使用します。
    """
    with patch("app.adapters.llm.ollama_client.Client") as mock_class:
        # Client() コンストラクタが返すインスタンスのモック
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        
        yield mock_class  # クラス(コンストラクタ)のモックを返す

# ----------------------------------------------------------------
# テストケース
# ----------------------------------------------------------------

@pytest.mark.asyncio
async def test_init_config(mock_ollama_lib): # 引数にフィクチャを追加(これでパッチが効く)
    """初期化: 環境変数の読み込み確認"""
    env_vars = {
        "OLLAMA_BASE_URL": "http://test-host:11434",
        "OLLAMA_MODEL": "test-model",
        "OLLAMA_ENABLE_THINKING": "true",
        "OLLAMA_ENABLE_STRUCTURED_OUTPUT": "false"
    }
    with patch.dict(os.environ, env_vars):
        client = OllamaClient()
        
        assert client.model_name == "test-model"
        assert client.enable_thinking is True
        assert client.enable_structured_output is False
        
        # モック（コンストラクタ）が正しいhostで呼ばれたか検証
        mock_ollama_lib.assert_called_with(host="http://test-host:11434")


@pytest.mark.asyncio
async def test_generate_text_with_thinking(mock_ollama_lib, capsys):
    """generate_text: Thinking有効時のストリーミング表示と回答取得"""
    # インスタンスのモックを取得
    mock_instance = mock_ollama_lib.return_value

    # Thinkingを有効化して初期化
    with patch.dict(os.environ, {"OLLAMA_ENABLE_THINKING": "true"}):
        client = OllamaClient()

    chunks = [
        create_mock_chunk(thinking="Hm,"),
        create_mock_chunk(thinking=" I think..."),
        create_mock_chunk(content="The answer "),
        create_mock_chunk(content="is 42."),
    ]
    # インスタンスの chat メソッドの戻り値を設定
    mock_instance.chat.return_value = iter(chunks)

    # 実行
    prompt = "Question?"
    result = await client.generate_text(prompt)

    # 検証
    assert result == "The answer is 42."

    captured = capsys.readouterr()
    assert "Hm, I think..." in captured.out
    
    # メソッド呼び出し検証
    mock_instance.chat.assert_called_with(
        model=ANY,
        messages=[{"role": "user", "content": prompt}],
        format=None,
        stream=True,
        options={"temperature": 0.7}
    )


@pytest.mark.asyncio
async def test_generate_json_structured_output_on(mock_ollama_lib):
    """generate_json: Structured Output有効時"""
    mock_instance = mock_ollama_lib.return_value

    with patch.dict(os.environ, {"OLLAMA_ENABLE_STRUCTURED_OUTPUT": "true"}):
        client = OllamaClient()

    expected_dict = {"summary": "test", "score": 100}
    
    mock_response = MagicMock()
    mock_response.message.content = json.dumps(expected_dict)
    
    # chatメソッドの戻り値を設定
    mock_instance.chat.return_value = mock_response

    result = await client.generate_json("Analyze", SampleSchema)

    assert result == expected_dict
    
    args, kwargs = mock_instance.chat.call_args
    assert kwargs["format"] == SampleSchema.model_json_schema()
    assert kwargs["stream"] is False


@pytest.mark.asyncio
async def test_generate_json_structured_output_off(mock_ollama_lib):
    """generate_json: Structured Output無効時"""
    mock_instance = mock_ollama_lib.return_value

    with patch.dict(os.environ, {"OLLAMA_ENABLE_STRUCTURED_OUTPUT": "false"}):
        client = OllamaClient()

    expected_dict = {"summary": "loose json", "score": 50}
    
    mock_response = MagicMock()
    mock_response.message.content = json.dumps(expected_dict)
    mock_instance.chat.return_value = mock_response

    result = await client.generate_json("Analyze", SampleSchema)

    assert result == expected_dict
    
    args, kwargs = mock_instance.chat.call_args
    assert kwargs["format"] == "json"


@pytest.mark.asyncio
async def test_generate_json_decode_error(mock_ollama_lib):
    """generate_json: 壊れたJSONが返ってきた場合"""
    mock_instance = mock_ollama_lib.return_value
    
    with patch.dict(os.environ, {"OLLAMA_ENABLE_STRUCTURED_OUTPUT": "true"}):
        client = OllamaClient()

    mock_response = MagicMock()
    mock_response.message.content = "{ invalid json ... "
    mock_instance.chat.return_value = mock_response

    with pytest.raises(json.JSONDecodeError):
        await client.generate_json("test", SampleSchema)