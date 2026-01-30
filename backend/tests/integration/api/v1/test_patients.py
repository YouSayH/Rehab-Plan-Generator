import pytest
from httpx import AsyncClient

# このマークをつけることで、async def のテスト関数が実行可能になります
@pytest.mark.asyncio
async def test_create_and_read_patient(async_client: AsyncClient):
    """
    正常系テスト: 患者を作成し、そのデータが取得できるか確認する
    """
    # 1. 新規登録 (POST)
    payload = {
        "hash_id": "test_auto_001",
        "age": 80,
        "gender": "女性",
        "diagnosis_code": "I61.0",
        "admission_date": "2026-02-01"
    }
    
    response = await async_client.post("/api/v1/patients/", json=payload)
    
    # アサーション（検証）
    assert response.status_code == 201, f"Create failed: {response.text}"
    data = response.json()
    assert data["hash_id"] == payload["hash_id"]
    assert data["age"] == payload["age"]
    assert "synced_at" in data

    # 2. 詳細取得 (GET)
    get_response = await async_client.get(f"/api/v1/patients/{payload['hash_id']}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["diagnosis_code"] == payload["diagnosis_code"]

@pytest.mark.asyncio
async def test_create_duplicate_patient(async_client: AsyncClient):
    """
    異常系テスト: 同じIDを登録しようとしたらエラーになるか
    """
    payload = {
        "hash_id": "test_duplicate_001",
        "age": 50,
        "gender": "男性"
    }
    
    # 1回目: 成功するはず
    res1 = await async_client.post("/api/v1/patients/", json=payload)
    assert res1.status_code == 201

    # 2回目: 400 Bad Requestになるはず
    res2 = await async_client.post("/api/v1/patients/", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]