from server import app
from fastapi.testclient import TestClient
import random
import pytest

client = TestClient(app)


@pytest.mark.dependency()
def test_create_correct():
    images = ['image.jpg', 'image.png']
    for i, image_name in enumerate(images):
        with open(f"test_media/{image_name}", "rb") as file:
            response = client.post("/memes?text=text", files={"file": (image_name, file)})
            response_body = response.json()
            assert response.status_code == 201
            assert response_body['meme_id'] > 0
            assert response_body['text'] == 'text'
            assert response_body['file_name'] == image_name


@pytest.mark.dependency(depends=['test_create_correct'])
def test_create_not_image():
    files = ['not_image.txt', 'large_not_image.txt']
    for i, file_name in enumerate(files):
        with open(f"test_media/{file_name}", "rb") as file:
            response = client.post("/memes?text=text",  files={"file": (file_name, file)})
            assert response.status_code == 415
            assert response.json()['detail'][0]['loc'] == ['body', 'file']


@pytest.mark.dependency(depends=['test_create_correct'])
def test_create_unsupported_image():
    file_name = "image.svg"
    with open(f"test_media/{file_name}", "rb") as file:
        response = client.post("/memes?text=text", files={"file": (file_name, file)})
        assert response.status_code == 415
        assert response.json()['detail'][0]['loc'] == ['body', 'file']


@pytest.mark.dependency(depends=['test_create_correct'])
def test_create_large_image():
    file_name = "very_large_image.jpg"
    with open(f"test_media/{file_name}", "rb") as file:
        response = client.post("/memes?text=text", files={"file": (file_name, file)})
        assert response.status_code == 413
        assert response.json()['detail'][0]['loc'] == ['body', 'file']


@pytest.mark.dependency(depends=['test_create_correct'])
def test_create_no_image():
    response = client.post("/memes?text=text", )
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ['body', 'file']


@pytest.mark.dependency(depends=['test_create_correct'])
def test_create_empty_text():
    file_name = "image.jpg"
    with open(f"test_media/{file_name}", "rb") as file:
        response = client.post("/memes?text=", files={"file": (file_name, file)})
        response_body = response.json()
        assert response.status_code == 422
        assert response_body['detail'][0]['loc'] == ['query', 'text']


@pytest.mark.dependency(depends=['test_create_correct'])
def test_create_very_long_text():
    file_name = "image.jpg"
    with open(f"test_media/{file_name}", "rb") as file:
        response = client.post(f"/memes?text={'X' * 2 ** 10}", files={"file": (file_name, file)})
        assert response.status_code == 422
        assert response.json()['detail'][0]['loc'] == ['query', 'text']


@pytest.mark.dependency(depends=['test_create_correct'])
def test_get_correct():
    file_name = "image.jpg"
    with open(f"test_media/{file_name}", "rb") as file:
        response = client.post("/memes?text=text", files={"file": (file_name, file)})
    print(response.json())
    response = client.get(f"/memes/{response.json()['meme_id']}")
    response_body = response.json()

    assert response.status_code == 200
    assert response_body['file_name'] == file_name
    assert response_body['text'] == 'text'
    assert response_body['mimetype'].startswith("image/")
    assert "url" in response_body


@pytest.mark.dependency(depends=['test_get_correct'])
def test_get_not_existed():
    meme_id = 123456
    response = client.get(f"/memes/{meme_id}")
    response_body = response.json()

    assert response.status_code == 404
    assert response_body['detail'][0]['loc'] == ['path', 'meme_id']
    assert response_body['detail'][0]['input'] == meme_id
    assert 'msg' in response_body['detail'][0]
    assert 'type' in response_body['detail'][0]


@pytest.mark.dependency(depends=['test_get_correct'])
def test_get_invalid_meme_id():
    meme_id = 'not-an-integer'
    response = client.get(f"/memes/{meme_id}")
    response_body = response.json()

    assert response.status_code == 422
    assert response_body['detail'][0]['loc'] == ['path', 'meme_id']
    assert response_body['detail'][0]['input'] == meme_id
    assert 'msg' in response_body['detail'][0]
    assert 'type' in response_body['detail'][0]


@pytest.mark.dependency(depends=['test_get_correct', 'test_create_correct'])
def test_get_all_correct():
    images = ['image.jpg', 'image.png'] * 3
    expected_answer = []
    min_meme_id = 9999999
    for i, image_name in enumerate(images):
        with open(f"test_media/{image_name}", "rb") as file:
            response = client.post("/memes?text=text", files={"file": (image_name, file)})
            response_body = response.json()
            min_meme_id = min(min_meme_id, response_body["meme_id"])
            expected_answer.append({
                "meme_id": response_body["meme_id"],
                "text": response_body["text"],
                "file_name": image_name,
                "mimetype": response_body["mimetype"]
            })
    limit = random.randint(2, len(images) - 1)
    response = client.get(f"/memes?offset={min_meme_id - 1}&limit={limit}")
    response_body = response.json()

    assert response.status_code == 200
    assert response_body == expected_answer[:limit]


@pytest.mark.dependency(depends=['test_get_all_correct'])
def test_get_all_empty():
    response = client.get(f"/memes?offset={10000}&limit={1}")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.dependency(depends=['test_get_correct', 'test_create_correct'])
def test_delete_correct():
    file_name = "image.jpg"
    with open(f"test_media/{file_name}", "rb") as file:
        response = client.post("/memes?text=text", files={"file": (file_name, file)})

    response = client.delete(f"/memes/{response.json()['meme_id']}")
    response_body = response.json()

    assert response.status_code == 200
    assert response_body['file_name'] == file_name
    assert response_body['text'] == 'text'
    assert response_body['mimetype'].startswith("image/")

    response = client.get(f"/memes/{response_body['meme_id']}")

    assert response.status_code == 404


@pytest.mark.dependency(depends=['test_delete_correct'])
def test_delete_not_existed():
    meme_id = 100000
    response = client.delete(f"/memes/{meme_id}")
    response_body = response.json()

    assert response.status_code == 404
    assert response_body['detail'][0]['loc'] == ['path', 'meme_id']
    assert response_body['detail'][0]['input'] == meme_id
    assert 'msg' in response_body['detail'][0]
    assert 'type' in response_body['detail'][0]


@pytest.mark.dependency(depends=['test_delete_correct'])
def test_delete_without_id():
    response = client.delete(f"/memes/")
    response_body = response.json()

    assert response.status_code == 405
    assert 'detail' in response_body


@pytest.mark.dependency(depends=['test_get_correct', 'test_create_correct'])
def test_put_text_correct():
    file_name = "image.jpg"
    with open(f"test_media/{file_name}", "rb") as file:
        response = client.post("/memes?text=text", files={"file": (file_name, file)}).json()
        meme_id = response['meme_id']
    response = client.put(f"/memes/{meme_id}?text=another")
    response_body_put = response.json()

    assert response.status_code == 200
    assert response_body_put['file_name'] == file_name
    assert response_body_put['text'] == 'another'
    assert response_body_put['mimetype'].startswith("image/")
    assert response_body_put['meme_id'] == meme_id

    response_body_get = client.get(f"/memes/{meme_id}").json()
    del response_body_get['url']

    assert response_body_get == response_body_put


@pytest.mark.dependency(depends=['test_put_text_correct'])
def test_put_text_incorrect():
    file_name = "image.jpg"
    with open(f"test_media/{file_name}", "rb") as file:
        response = client.post("/memes?text=text", files={"file": (file_name, file)}).json()
        meme_id = response['meme_id']

    texts = ["", "X" * 1024]
    for text in texts:
        response = client.put(f"/memes/{meme_id}?text={text}")
        response_body = response.json()

        assert response.status_code == 422
        assert response_body['detail'][0]['loc'] == ['query', 'text']


@pytest.mark.dependency(depends=['test_get_correct', 'test_create_correct'])
def test_put_image_correct():
    file_name = "image.jpg"
    with open(f"test_media/{file_name}", "rb") as file:
        response_body_post = client.post("/memes?text=text", files={"file": (file_name, file)}).json()
        meme_id = response_body_post['meme_id']

    new_file_name = "image.png"
    with open(f"test_media/{file_name}", "rb") as file:
        response = client.put(f"/memes/{meme_id}", files={"file": (new_file_name, file)})
    response_body_put = response.json()

    assert response.status_code == 200
    assert response_body_put['file_name'] != response_body_post['file_name']
    assert response_body_put['text'] == response_body_post['text']
    assert response_body_put['meme_id'] == meme_id


@pytest.mark.dependency(depends=['test_put_image_correct'])
def test_put_image_incorrect():
    file_name = "image.jpg"
    with open(f"test_media/{file_name}", "rb") as file:
        response_body_post = client.post("/memes?text=text", files={"file": (file_name, file)}).json()
        meme_id = response_body_post['meme_id']

    new_file_name = "not_image.txt"
    with open(f"test_media/{file_name}", "rb") as file:
        response = client.put(f"/memes/{meme_id}", files={"file": (new_file_name, file)})
    response_body_put = response.json()

    assert response.status_code == 415
    assert response_body_put['detail'][0]['loc'] == ['body', 'file']


@pytest.mark.dependency(depends=['test_put_image_correct'])
def test_put_image_large():
    file_name = "image.jpg"
    with open(f"test_media/{file_name}", "rb") as file:
        response_body_post = client.post("/memes?text=text", files={"file": (file_name, file)}).json()
        meme_id = response_body_post['meme_id']

    new_file_name = "very_large_image.jpg"
    with open(f"test_media/{new_file_name}", "rb") as file:
        response = client.put(f"/memes/{meme_id}", files={"file": (new_file_name, file)})
    response_body_put = response.json()

    assert response.status_code == 413
    assert response_body_put['detail'][0]['loc'] == ['body', 'file']
