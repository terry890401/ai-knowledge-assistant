from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

# 測試前先登入取得 token
def get_token():
    client.post("/auth/register", json={
        "email": "doc_test@test.com",
        "password": "testpassword123"
    })
    response = client.post("/auth/login", json={
        "email": "doc_test@test.com",
        "password": "testpassword123"
    })
    return response.json()["access_token"]

# 測試上傳文件
def test_upload_document():
    token = get_token()
    # 建立假的 txt 文件
    file_content = b"This is test file content for upload testing."
    response = client.post("/documents/",
        files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "test.txt"

# 測試取得文件列表
def test_get_documents():
    token = get_token()
    response = client.get("/documents/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 測試刪除文件
def test_delete_document():
    token = get_token()
    # 先上傳文件
    file_content = b"Test file to be deleted."
    upload_response = client.post("/documents/",
        files={"file": ("delete_test.txt", io.BytesIO(file_content), "text/plain")},
        headers={"Authorization": f"Bearer {token}"}
    )
    doc_id = upload_response.json()["id"]

    # 刪除文件
    response = client.delete(f"/documents/{doc_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

# 測試未登入無法存取
def test_documents_unauthorized():
    response = client.get("/documents/")
    assert response.status_code == 401
