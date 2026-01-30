from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.database import AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPIのDependency（依存性注入）用関数。
    APIリクエストの処理中に使用するDBセッションを作成し、処理終了後に確実にクローズします。
    """
    # デバッグ用: セッション開始ログ
    print("[dependencies] Creating new DB session...")
    
    # AsyncSessionLocal() で新しいセッションを生成
    async with AsyncSessionLocal() as session:
        try:
            # APIのエンドポイントにセッションを渡す（yield）
            yield session
        except Exception as e:
            print(f"[dependencies] Error in DB session: {e}")
            raise
        finally:
            # 処理終了後（またはエラー発生後）に必ずここに戻ってきてセッションを閉じる
            print("[dependencies] Closing DB session.")
            await session.close()