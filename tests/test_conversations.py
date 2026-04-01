from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 測試前先登入取得 token
def get_token():
    # 確保測試帳號存在
    client.post("/auth/register", json={
        "email": "conv_test@test.com",
        "password": "testpassword123"
    })
    response = client.post("/auth/login", json={
        "email": "conv_test@test.com",
        "password": "testpassword123"
    })
    return response.json()["access_token"]

# 測試新增對話
def test_create_conversation():
    token = get_token()
    response = client.post("/conversations/",
        json={"title": "測試對話"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "測試對話"

# 測試取得對話列表
def test_get_conversations():
    token = get_token()
    response = client.get("/conversations/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 測試取得單一對話
def test_get_conversation_detail():
    token = get_token()
    # 先建立對話
    create_response = client.post("/conversations/",
        json={"title": "單一對話測試"},
        headers={"Authorization": f"Bearer {token}"}
    )
    conv_id = create_response.json()["id"]

    # 取得對話詳細
    response = client.get(f"/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == conv_id
    assert "messages" in response.json()

# 測試刪除對話
def test_delete_conversation():
    token = get_token()
    # 先建立對話
    create_response = client.post("/conversations/",
        json={"title": "要刪除的對話"},
        headers={"Authorization": f"Bearer {token}"}
    )
    conv_id = create_response.json()["id"]

    # 刪除對話
    response = client.delete(f"/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

# 測試未登入無法存取
def test_unauthorized():
    response = client.get("/conversations/")
    assert response.status_code == 401
