import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# ロギング設定
logger = logging.getLogger(__name__)

# 環境変数からDB接続URLを取得
# 万が一設定がない場合は、デフォルト値として開発用の設定を使用します
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/rehab_db")

# セキュリティのため、パスワード部分を隠して接続先をログ出力（デバッグ用）
safe_url = DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else "UNKNOWN"
print(f"[{__name__}] Loading Database URL for: {safe_url}")

# 非同期エンジンの作成
# echo=True にすることで、実行されたSQLクエリがコンソールに表示されます（デバッグに最適）
engine = create_async_engine(
    DATABASE_URL,
    echo=True, 
    future=True,
)

# 非同期セッションファクトリの作成
# APIリクエストのたびに、この工場から新しいセッション（DBへの接続口）が生み出されます
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

print(f"[{__name__}] Async Database Engine initialized successfully.")