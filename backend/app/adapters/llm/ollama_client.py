import asyncio
import json
import os
import sys
from typing import Any, Dict, Type

from ollama import Client
from pydantic import BaseModel

from .base import LLMClient


class OllamaClient(LLMClient):
    """
    Ollama (公式Pythonライブラリ) 用のLLMクライアント実装。
    Thinking Models (思考プロセス) のストリーミング表示や、
    構造化出力 (Structured Outputs) のオンオフ制御に対応しています。

    Attributes:
        client (ollama.Client): Ollamaクライアントインスタンス。
        model_name (str): 使用するモデル名。
        enable_thinking (bool): Thinking機能（思考プロセスの表示）を有効にするか。
        enable_structured_output (bool): JSON Schemaによる厳格な構造化出力を有効にするか。
    """

    def __init__(self):
        """
        環境変数から設定を取得して初期化します。
        
        ENV Variables:
            OLLAMA_BASE_URL: 接続先 (default: http://localhost:11434)
            OLLAMA_MODEL: モデル名 (default: qwen3:0.6b)
            OLLAMA_ENABLE_THINKING: "true"で思考プロセスを表示 (default: false)
            OLLAMA_ENABLE_STRUCTURED_OUTPUT: "true"でSchema強制モード有効 (default: true)
        """
        host = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.client = Client(host=host)
        
        self.model_name = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
        
        # 機能トグル (文字列判定)
        self.enable_thinking = os.getenv("OLLAMA_ENABLE_THINKING", "false").lower() == "true"
        self.enable_structured_output = os.getenv("OLLAMA_ENABLE_STRUCTURED_OUTPUT", "true").lower() == "true"

        print(f"[OllamaClient] Initialized: {self.model_name} @ {host}")
        print(f"               Thinking: {self.enable_thinking}, StructuredOutput: {self.enable_structured_output}")

    def _run_chat_stream(self, messages: list, format_schema: Any = None) -> str:
        """
        同期的なチャット処理を実行する内部メソッド。
        Thinking機能が有効な場合はストリーミングで思考を表示します。
        
        Args:
            messages: チャットメッセージリスト
            format_schema: JSON Schema (Structured Output用) または 'json' 文字列

        Returns:
            str: 最終的な生成コンテンツ
        """
        # Thinking有効時はストリーミングを強制
        stream = self.enable_thinking
        
        # Thinkingに対応していないモデルでstream=Trueにしてもエラーにはならない
        # API呼び出し
        response_iter = self.client.chat(
            model=self.model_name,
            messages=messages,
            format=format_schema,
            stream=stream,
            options={"temperature": 0.7}
        )

        if not stream:
            # ストリーミングしない場合は一括取得 (.message.content)
            return response_iter.message.content

        # ストリーミング処理 (思考ログ表示 + コンテンツ蓄積)
        final_content = []
        print("\n[Thinking] ", end="", flush=True)

        try:
            for chunk in response_iter:
                # 思考プロセスの表示 (Thinking Models support)
                # chunk.message.thinking が存在すれば出力
                if hasattr(chunk.message, 'thinking') and chunk.message.thinking:
                    sys.stdout.write(chunk.message.thinking)
                    sys.stdout.flush()
                
                # 最終回答の蓄積
                if chunk.message.content:
                    final_content.append(chunk.message.content)
        finally:
            print("\n[Thinking End]\n", flush=True)

        return "".join(final_content)

    async def generate_text(self, prompt: str) -> str:
        """
        Ollamaを用いてテキストを生成します。
        """
        print(f"[OllamaClient] Generating text with {self.model_name}...")
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            # スレッドプールで実行して非同期化
            content = await asyncio.to_thread(
                self._run_chat_stream, 
                messages=messages, 
                format_schema=None
            )
            return content

        except Exception as e:
            print(f"[OllamaClient] Error generating text: {e}")
            raise

    async def generate_json(self, prompt: str, schema: Type[BaseModel]) -> Dict[str, Any]:
        """
        Ollamaを用いてJSONデータを生成します。
        enable_structured_outputの設定により挙動が変わります。
        """
        print(f"[OllamaClient] Generating JSON with {self.model_name}...")

        # 1. Structured Output設定の判定
        if self.enable_structured_output:
            # Pydanticスキーマを渡して構造を強制
            format_arg = schema.model_json_schema()
            final_prompt = prompt
        else:
            # 汎用JSONモード + プロンプトエンジニアリング
            format_arg = "json"
            # スキーマ情報をプロンプトに注入して指示
            schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
            final_prompt = (
                f"{prompt}\n\n"
                f"IMPORTANT: Output strictly in JSON format following this schema:\n"
                f"{schema_json}"
            )

        messages = [{"role": "user", "content": final_prompt}]

        try:
            # スレッドプールで実行
            json_str = await asyncio.to_thread(
                self._run_chat_stream,
                messages=messages,
                format_schema=format_arg
            )
            
            # JSONパース
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                print(f"[OllamaClient] JSON Decode Error. Response: {json_str[:200]}...")
                raise

        except Exception as e:
            print(f"[OllamaClient] Error generating JSON: {e}")
            raise