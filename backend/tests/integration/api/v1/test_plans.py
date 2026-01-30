import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_read_plan(async_client: AsyncClient):
    """
    正常系: 患者を作成し、その患者に紐づく計画書を作成・取得できるか
    """
    # 1. 前提となる患者を作成
    patient_payload = {
        "hash_id": "plan_test_patient_01",
        "age": 70,
        "gender": "女性",
        "admission_date": "2026-03-01"
    }
    await async_client.post("/api/v1/patients/", json=patient_payload)

    # 2. 計画書を作成 (POST)
    plan_payload = {
        "hash_id": patient_payload["hash_id"],
        "doc_date": "2026-03-05",
        "format_version": "v1.0",
        "raw_data": {
            "adl_score": 50,
            "target": "Walking with cane",
            "remarks": "元気です"
        }
    }
    
    response = await async_client.post("/api/v1/plans/", json=plan_payload)
    assert response.status_code == 201
    data = response.json()
    
    # JSONデータがそのまま保存されているか確認
    assert data["raw_data"]["target"] == "Walking with cane"
    plan_id = data["plan_id"]

    # 3. 取得 (GET by ID)
    get_res = await async_client.get(f"/api/v1/plans/{plan_id}")
    assert get_res.status_code == 200
    assert get_res.json()["raw_data"]["adl_score"] == 50

@pytest.mark.asyncio
async def test_update_plan(async_client: AsyncClient):
    """
    正常系: 計画書の内容(JSON)を更新できるか
    """
    # 1. 患者と計画書の準備
    pid = "plan_test_update_01"
    await async_client.post("/api/v1/patients/", json={"hash_id": pid})
    
    create_res = await async_client.post("/api/v1/plans/", json={
        "hash_id": pid,
        "raw_data": {"status": "before"}
    })
    plan_id = create_res.json()["plan_id"]

    # 2. 更新 (PUT)
    update_payload = {
        "raw_data": {"status": "after", "new_field": "added"}
    }
    update_res = await async_client.put(f"/api/v1/plans/{plan_id}", json=update_payload)
    assert update_res.status_code == 200
    
    # 3. 確認
    assert update_res.json()["raw_data"]["status"] == "after"
    assert update_res.json()["raw_data"]["new_field"] == "added"