"""
File: backend/app/main.py

Summary:
FastAPIアプリケーションのメインエントリーポイントとなるファイル。
APIサーバーの初期化、CORS（Cross-Origin Resource Sharing）のミドルウェア設定、および各機能層（患者情報、計画書、テンプレート）のルーター登録を行っています。フロントエンドからのAPIリクエストを受け取り、適切なエンドポイント群へ処理を振り分ける「交通整理」の役割を担う、システム全体の起点です。

Tags: FastAPI, Entry Point, CORS, Router Registration, API Server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 作成したルーターをインポート
from app.api.v1.endpoints import patients, plans, templates

app = FastAPI(
    title="Rehab Plan Generator API",
    version="0.1.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------
# ルーターの登録 (Router Registration)
# ----------------------------------------------------------------
# これにより、patients.py で定義した機能が以下のURLで有効になります
# - POST: http://localhost:8000/api/v1/patients/
# - GET : http://localhost:8000/api/v1/patients/
# ----------------------------------------------------------------
app.include_router(patients.router, prefix="/api/v1/patients", tags=["patients"])
app.include_router(plans.router, prefix="/api/v1/plans", tags=["plans"])
# テンプレート用ルーターを登録
app.include_router(templates.router, prefix="/api/v1/templates", tags=["templates"])

# 既存のエンドポイント
@app.get("/api/")
def read_root():
    return {"message": "Hello from FastAPI!", "status": "running"}

# ヘルスチェック用
@app.get("/api/health")
def health_check():
    return {"status": "ok", "db": "unknown"}