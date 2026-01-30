import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ----------------------------------------------------------------
# 1. モデル定義のインポート
# ----------------------------------------------------------------
# Docker内であれば app パッケージが見えるため、これでモデルを認識させます
from app.infrastructure.db.models import Base

# ----------------------------------------------------------------
# 2. 設定の読み込み
# ----------------------------------------------------------------
config = context.config

# ログ設定を適用
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ----------------------------------------------------------------
# 3. データベースURLの取得
# ----------------------------------------------------------------
# 環境変数 DATABASE_URL を優先して使用するロジック
# alembic.ini に書かれているダミーURLはここで無視されます
def get_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        # 環境変数がない場合のフォールバック（開発用デフォルト）
        return "postgresql+asyncpg://user:password@db:5432/rehab_db"
    return url

# Base.metadata をセットすることで、モデル定義とDBの差分を検知できるようになります
target_metadata = Base.metadata

# ----------------------------------------------------------------
# 4. マイグレーション実行ロジック (非同期対応)
# ----------------------------------------------------------------

def run_migrations_offline() -> None:
    """オフラインモード: DB接続せずにSQLスクリプトのみ生成する場合"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """同期コンテキスト内でマイグレーションを実行するヘルパー"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """オンラインモード: 非同期エンジンを使ってマイグレーションを実行"""
    
    # 設定オブジェクトを作成し、URLを環境変数から上書き
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    # 非同期エンジン (AsyncEngine) を作成
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # 非同期コネクションを使って、同期的なマイグレーション関数を実行
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # AsyncIOイベントループ上で実行
    asyncio.run(run_migrations_online())