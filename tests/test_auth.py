from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 測試註冊成功
def test_register_success():
    response = client.post("/auth/register", json={
        "email": "brand_newsssss@test.com",
        "password": "testpassword123"
    })
    assert response.status_code == 201
    assert "email" in response.json()

# 測試重複 email 註冊
def test_register_duplicate_email():
    # 先註冊一次
    client.post("/auth/register", json={
        "email": "duplicate@test.com",
        "password": "testpassword123"
    })
    # 再註冊一次，應該回傳 409
    response = client.post("/auth/register", json={
        "email": "duplicate@test.com",
        "password": "testpassword123"
    })
    assert response.status_code == 409

# 測試登入成功
def test_login_success():
    # 先註冊
    client.post("/auth/register", json={
        "email": "login_test@test.com",
        "password": "testpassword123"
    })
    # 再登入
    response = client.post("/auth/login", json={
        "email": "login_test@test.com",
        "password": "testpassword123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

# 測試錯誤密碼
def test_login_wrong_password():
    response = client.post("/auth/login", json={
        "email": "pytest_test@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401