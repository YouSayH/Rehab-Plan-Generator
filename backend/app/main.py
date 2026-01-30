from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 作成したルーターをインポート
from app.api.v1.endpoints import patients, plans

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

# 既存のエンドポイント
@app.get("/api/")
def read_root():
    return {"message": "Hello from FastAPI!", "status": "running"}

# ヘルスチェック用
@app.get("/api/health")
def health_check():
    return {"status": "ok", "db": "unknown"}