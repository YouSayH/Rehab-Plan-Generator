from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# 修正ポイント: パスを "/" ではなく "/api/" に変更、または追加します
@app.get("/api/")
def read_root():
    return {"message": "Hello from FastAPI!", "status": "running"}

# ヘルスチェック用
@app.get("/api/health")
def health_check():
    return {"status": "ok", "db": "unknown"}