"""
File: backend/tests/conftest.py

Summary:
Pytestを用いた自動テストのための共通設定とフィクスチャ（テスト用部品）を定義するファイル。
テスト実行時に一時的な非同期データベースセッション（`db_session`）を構築し、テストが完了するたびにロールバック（変更の取り消し）を行うことで、テスト間のデータ干渉を防ぎます。また、FastAPIの依存性注入（`get_db`）をテスト用セッションにオーバーライドし、実際のサーバーを立ち上げることなくAPIエンドポイントをテストできる非同期クライアント（`async_client`）を提供します。

Tags: Test, Pytest, Fixture, Database, AsyncClient, FastAPI
"""

import sys
import os
import pytest_asyncio
from typing import AsyncGenerator
# ASGITransport を忘れずに
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

# ========================================================
# パス解決ロジック
# ========================================================
current_file = os.path.abspath(__file__)
tests_dir = os.path.dirname(current_file)
project_root = os.path.dirname(tests_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ========================================================
# アプリケーションのインポート
# ========================================================
from app.main import app
from app.infrastructure.db.database import DATABASE_URL
from app.api.dependencies import get_db

# ========================================================
# テスト用設定 (Fixtures)
# ========================================================

# これにより、テストごとに接続が完全に切断され、イベントループのエラーを防ぎます
engine = create_async_engine(DATABASE_URL, echo=False, poolclass=NullPool)

TestingSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = TestingSessionLocal(bind=connection)
        yield session
        await session.close()
        await transaction.rollback()

@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()