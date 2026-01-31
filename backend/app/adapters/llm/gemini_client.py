import asyncio
import json
import os
from typing import Any, Dict, Type

from google import genai
from google.genai import types
from pydantic import BaseModel

from .base import LLMClient


class GeminiClient(LLMClient):
    """
    Google Gemini (新ライブラリ google-genai) 用のLLMクライアント実装。

    Attributes:
        client (genai.Client): Google GenAI SDKのクライアントインスタンス。
        model_name (str): 使用するモデル名 (デフォルト: gemini-2.5-flash-lite)。
    """

    def __init__(self):
        """
        環境変数からAPIキーとモデル名を取得して初期化します。
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # 開発時の警告用（本番ではログ出力を推奨）
            print("[GeminiClient] Warning: GEMINI_API_KEY is not set.")

        self.client = genai.Client(api_key=api_key)

        # 指定されたモデル名を使用 (デフォルトは gemini-2.5-flash-lite)
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        print(f"[GeminiClient] Initialized with model: {self.model_name} (google-genai)")

    async def generate_text(self, prompt: str) -> str:
        """
        Geminiを用いてテキストを生成します。
        SDKの同期メソッドを asyncio.to_thread でラップして非同期実行します。

        Args:
            prompt (str): 入力プロンプト。

        Returns:
            str: 生成されたテキスト。
        """
        print(f"[GeminiClient] Generating text with {self.model_name}...")

        try:
            # 同期メソッドを別スレッドで実行し、イベントループをブロックしないようにする
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7
                ),
            )
            return response.text

        except Exception as e:
            print(f"[GeminiClient] Error generating text: {e}")
            raise

    async def generate_json(
        self, prompt: str, schema: Type[BaseModel]
    ) -> Dict[str, Any]:
        """
        Geminiを用いてPydanticスキーマに基づいたJSONデータを生成します。
        Structured Outputs (response_json_schema) 機能を利用します。

        Args:
            prompt (str): 入力プロンプト。
            schema (Type[BaseModel]): 出力構造を定義するPydanticモデル。

        Returns:
            Dict[str, Any]: 生成されたJSONデータ。
        """
        print(f"[GeminiClient] Generating JSON with {self.model_name}...")

        try:
            # 構造化出力の設定
            # response_mime_type と response_json_schema を指定することで
            # モデルが強制的にスキーマに従ったJSONを出力する
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=schema.model_json_schema(),
                temperature=0.7,
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=config,
            )

            # レスポンスがJSON文字列として返ってくるため、パースして辞書で返す
            # Pydanticモデルでのバリデーションは呼び出し元で行う想定だが、
            # ここでは純粋なDictを返す契約とする
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                # 万が一JSON以外が返ってきた場合のフェイルセーフ
                # Pydanticの `model_validate_json` を使う手もあるが、
                # インターフェース定義 (Dict返却) に合わせる
                print(f"[GeminiClient] JSON Decode Error. Response: {response.text}")
                raise

        except Exception as e:
            print(f"[GeminiClient] Error generating JSON: {e}")
            raise