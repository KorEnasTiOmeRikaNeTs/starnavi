# tests/test_api.py

import os
import pytest

from jose import jwt

from models import Posts


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


# scope="module"
@pytest.fixture() 
def create_post(create_test_user, db, client):
    user = create_test_user
    payload = {"sub": user.username, "id": user.id}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    post_data = {
        "title": "Christmas 2024",
        "content": """
            Christmas 2024 is here, bringing warmth, joy, and the spirit of giving. It is a time to celebrate with family, friends, and loved ones, reflecting on the blessings of the past year. This season reminds us of the importance of kindness and sharing, as we exchange gifts, enjoy festive meals, and cherish moments together.
            The world glows with twinkling lights and decorations, filling hearts with hope and wonder. As we gather around trees and fireplaces, let us embrace the true meaning of Christmas: love, unity, and peace. Here is to a magical holiday season and a brighter year ahead.
        """,
    }
    response = client.post(
        "/posts/create-post",
        json=post_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    return response, user


# Тест на створення поста
def test_create_post(create_post, db):
    response, user = create_post
    assert response.status_code == 201

    # Перевірка створеного поста в базі даних
    post = db.query(Posts).filter(Posts.title == "Christmas 2024").first()
    assert post is not None
    assert post.title == "Christmas 2024"


# Тест на оновлення поста
def test_update_post(create_post, db, client):
    response, user = create_post

    post = db.query(Posts).filter(Posts.title == "Christmas 2024").first()

    payload = {"sub": user.username, "id": user.id}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    updated_data = {
        "title": "Updated Test Post",
        "content": "This is an updated test post.",
    }
    response = client.put(
        f"/posts/{post.id}/update-post",
        json=updated_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    updated_post = db.query(Posts).filter(Posts.id == post.id).first()
    assert updated_post.title == "Updated Test Post"


# Тест на видалення поста
def test_delete_post(create_post, db, client):
    _, user = create_post

    post = db.query(Posts).filter(Posts.title == "Christmas 2024").first()

    payload = {"sub": user.username, "id": user.id}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    response = client.delete(
        f"/posts/{post.id}/delete", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    deleted_post = db.query(Posts).filter(Posts.id == post.id).first()
    assert deleted_post is None
