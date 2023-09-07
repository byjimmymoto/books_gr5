import os
from fastapi.testclient import TestClient
from app.main import app
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "../.env"))

client = TestClient(app)


def user_authentication_headers(email: str, password: str):
    data = {"username": email, "password": password}
    r = client.post("/login", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def test_read_root():
    response = client.get("/documentation")
    assert response.status_code == 200


def test_create_book():
    headers = user_authentication_headers(os.environ['TEST_USER'], os.environ['TEST_PASS'])
    sample_payload = {
          "id": 0,
          "title": "Book Test",
          "subtitle": "book",
          "publish_date": 2023,
          "description": "This is description of book test",
          "thumbnail": "https://kffhealthnews.org/wp-content/uploads/sites/2/2018/04/surgery.jpg",
          "publishers": [
            {
              "id": 0,
              "name": "Test publisher"
            }
          ],
          "authors": [
            {
              "name": "Test author",
              "id": 0
            }
          ],
          "genres": [
            {
              "name": "Test genres",
              "id": 0
            }
          ]
        }
    response = client.post("/book/", json=sample_payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == {
          "usuario": os.environ['TEST_USER'],
          "engine": "Local"
        }