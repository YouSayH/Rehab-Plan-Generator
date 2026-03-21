"""
File: backend/app/adapters/llm/base.py

Summary:
LLMクライアントの抽象基底クラス（インターフェース）を定義するファイル。
システム全体で利用する様々なLLM（GeminiやOllamaなど）の共通仕様を定めています。
具体的には、単純なテキスト生成を行う `generate_text` と、Pydanticスキーマに基づいてJSON形式の構造化データを生成する `generate_json` の2つの抽象メソッドを定義し、具象クラスでの実装を強制しています。

Tags: LLM, Adapter, Interface, Abstract Base Class
"""
import abc
from typing import Any, Dict, Type

from pydantic import BaseModel


class LLMClient(abc.ABC):
    """
    LLMクライアントの抽象基底クラス (Interface)。
    全ての具体的なクライアント（Gemini, Ollama等）はこのクラスを継承し、
    定義されたメソッドを実装する必要があります。
    """

    @abc.abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """
        プロンプトに基づいて単純なテキスト生成を行います。

        Args:
            prompt (str): LLMへの入力プロンプト。

        Returns:
            str: 生成されたテキスト。
        """
        pass

    @abc.abstractmethod
    async def generate_json(self, prompt: str, schema: Type[BaseModel]) -> Dict[str, Any]:
        """
        Pydanticスキーマに基づいた構造化データ（JSON）を生成して返します。

        Args:
            prompt (str): LLMへの入力プロンプト。
            schema (Type[BaseModel]): 出力の構造を定義するPydanticモデルクラス。

        Returns:
            Dict[str, Any]: 生成されたJSONデータ（辞書形式）。
        """
        pass