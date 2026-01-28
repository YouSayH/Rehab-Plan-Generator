# ----------------------------------------------------------------
# 1. Base Image
# ----------------------------------------------------------------
# Python 3.11 の軽量版(slim)を使用
FROM python:3.11-slim

# コンテナ内の作業ディレクトリを設定
WORKDIR /app

# ----------------------------------------------------------------
# 2. System Dependencies
# ----------------------------------------------------------------
# ビルドに必要なツールや、ヘルスチェック用の curl をインストール
# rm -rf でキャッシュを削除してイメージサイズを削減
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------------
# 3. Package Manager (uv) Setup
# ----------------------------------------------------------------
# 公式イメージから uv コマンドだけをコピー（これが一番速くて安全）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# ----------------------------------------------------------------
# 4. Install Dependencies
# ----------------------------------------------------------------
# まず依存関係ファイルだけをコピー（キャッシュを効かせるため）
COPY pyproject.toml .
# フォルダごとコピーする必要がある場合
COPY requirements/ ./requirements/

# ライブラリのインストール
# --system: 仮想環境を作らずコンテナのPythonに直接入れる設定
# 開発中は dev 依存関係も含めたいので、必要に応じてフラグを調整
RUN uv pip install --system fastapi uvicorn[standard] sqlalchemy asyncpg psycopg2-binary httpx python-multipart

# ※ 本格的な運用では pyproject.toml に依存関係を書き、
# RUN uv pip install --system -r pyproject.toml とします。
# 今回は初期セットアップのため、主要ライブラリを直接入れています。

# ----------------------------------------------------------------
# 5. Runtime Config
# ----------------------------------------------------------------
# アプリケーションコードは docker-compose でマウントするので、
# ここでの COPY は不要（本番ビルド時は COPY . . が必要）

# 環境変数の設定（Pythonのバッファリングを無効化してログを即時出力）
ENV PYTHONUNBUFFERED=1

# コンテナ起動時のコマンド（compose.yamlの設定が優先されますが一応記述）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]