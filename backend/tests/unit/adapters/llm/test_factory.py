import os
import pytest
from unittest.mock import patch

from app.adapters.llm.factory import get_llm_client
from app.adapters.llm.gemini_client import GeminiClient
from app.adapters.llm.ollama_client import OllamaClient


@pytest.fixture(autouse=True)
def clear_cache():
    """
    各テスト実行前に lru_cache をクリアするFixture。
    これを行わないと、前のテストで作られたインスタンスが残り続け、
    環境変数を切り替えても反映されなくなります。
    """
    get_llm_client.cache_clear()
    yield
    get_llm_client.cache_clear()


@pytest.fixture(autouse=True)
def setup_env():
    """
    GeminiClientの初期化に必要なダミー環境変数をセットします。
    これを設定しないと google-genai ライブラリが初期化エラー(ValueError)を起こします。
    """
    with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy_key_for_test"}):
        yield


def test_get_client_gemini():
    """LLM_PROVIDER='gemini' の場合、GeminiClientが返ること"""
    with patch.dict(os.environ, {"LLM_PROVIDER": "gemini"}):
        client = get_llm_client()
        assert isinstance(client, GeminiClient)


def test_get_client_ollama():
    """LLM_PROVIDER='ollama' の場合、OllamaClientが返ること"""
    with patch.dict(os.environ, {"LLM_PROVIDER": "ollama"}):
        client = get_llm_client()
        assert isinstance(client, OllamaClient)


def test_get_client_fallback_default():
    """想定外のプロバイダ名の場合、デフォルト（Gemini）にフォールバックすること"""
    with patch.dict(os.environ, {"LLM_PROVIDER": "unknown_x"}):
        client = get_llm_client()
        # 警告ログが出ているはずだが、動作としてはGeminiを返す
        assert isinstance(client, GeminiClient)


def test_get_client_singleton_behavior():
    """シングルトン（キャッシュ）の動作確認"""
    with patch.dict(os.environ, {"LLM_PROVIDER": "gemini"}):
        client1 = get_llm_client()
        client2 = get_llm_client()

        # 2回呼んでも、ID（メモリアドレス）が同じインスタンスであること
        assert client1 is client2
        
        # 型の確認
        assert isinstance(client1, GeminiClient)