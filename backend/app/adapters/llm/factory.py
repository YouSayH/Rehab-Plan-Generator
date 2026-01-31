import os
from functools import lru_cache

from .base import LLMClient
from .gemini_client import GeminiClient
from .ollama_client import OllamaClient


@lru_cache()
def get_llm_client() -> LLMClient:
    """
    環境変数 LLM_PROVIDER に基づいて適切なLLMクライアントを生成・返却します。
    @lru_cache デコレータにより、一度生成したインスタンスをキャッシュ（シングルトン化）し、
    アプリケーション全体で再利用します。

    Returns:
        LLMClient: 具体的な実装クラス（GeminiClient または OllamaClient）のインスタンス。
    """
    # デフォルトは gemini (クラウド) とします
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    print(f"[LLM Factory] Creating client for provider: {provider}")

    if provider == "gemini":
        return GeminiClient()
    elif provider == "ollama":
        return OllamaClient()
    else:
        # 想定外の値が設定されている場合は、安全のためデフォルト(Gemini)にフォールバックします
        print(f"[LLM Factory] Warning: Unknown provider '{provider}'. Falling back to Gemini.")
        return GeminiClient()