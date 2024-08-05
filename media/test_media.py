from server import app
from fastapi.testclient import TestClient
import pytest


client = TestClient(app)


@pytest.mark.dependency()
def test_connection():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"detail": [{"msg": "ok"}]}


@pytest.mark.dependency(depends=["test_connection"])
@pytest.mark.dependency()
def test_not_existing_file():
    response = client.get("/abracadabra")
    assert response.status_code == 404
    assert response.json() == {"detail": [{"msg": "File not exists"}]}


@pytest.mark.dependency(depends=["test_connection"])
def test_delete_not_existing_file():
    response = client.delete("/abracadabra")
    assert response.status_code == 404
    assert response.json() == {"detail": [{"msg": "File not exists"}]}


@pytest.mark.dependency(depends=["test_connection"])
def test_create_file():
    test_files = ["image.jpg", "large_not_image.txt"]

    for test_filename in test_files:
        with open(f"test_media/{test_filename}", "rb") as file:
            response = client.post("/",
                                   files={"file": (test_filename, file)})

            assert response.status_code == 201
            assert response.json()['detail'][0]['msg'] == 'File created'
            assert "bucket_name" in response.json()['detail'][0]
            assert "file_name" in response.json()['detail'][0]


@pytest.mark.dependency(depends=["test_create_file"])
def test_create_and_get():
    test_filename = "test_media/image.jpg"
    response = client.post("/",
                           files={"file": (test_filename, open(test_filename, "rb"))})

    filename = response.json()['detail'][0]['file_name']

    response = client.get(f"/{filename}")

    assert response.status_code == 200
    assert response.json()['detail'][0]['msg'] == 'ok'
    assert "url" in response.json()['detail'][0]


@pytest.mark.dependency(depends=["test_create_file"])
def test_create_and_delete():
    test_filename = "test_media/image.jpg"
    response = client.post("/",
                           files={"file": (test_filename, open(test_filename, "rb"))})

    filename = response.json()['detail'][0]['file_name']

    response = client.delete(f"/{filename}")

    assert response.status_code == 200
    assert response.json()['detail'][0]['msg'] == 'ok'


@pytest.mark.dependency(depends=["test_create_file", "test_create_and_delete"])
def test_get_after_delete():
    test_filename = "test_media/image.jpg"
    response = client.post("/",
                           files={"file": (test_filename, open(test_filename, "rb"))})

    filename = response.json()['detail'][0]['file_name']
    response = client.delete(f"/{filename}")
    response = client.get(f"/{filename}")

    assert response.status_code == 404
    assert response.json() == {"detail": [{"msg": "File not exists"}]}


@pytest.mark.dependency(depends=["test_create_file"])
def test_empty_create_file():

    response = client.post("/")

    assert response.status_code == 422


@pytest.mark.dependency(depends=["test_create_and_delete"])
def test_empty_delete_file():

    response = client.delete("/")

    assert response.status_code == 405
