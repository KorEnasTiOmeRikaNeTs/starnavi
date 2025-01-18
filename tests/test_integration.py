# tests/test_integration.py

import os
import pytest

from jose import jwt

from models import Users


def test_auth_to_login(db, client):
    response = client.post(
        "auth/register",
        json={
            "email": "anastas@gmain.com",
            "username": "supernastya",
            "password": "hashedpassword",
        },
    )
    assert response.status_code == 201

    user = db.query(Users).filter(Users.username == "supernastya").first()
    assert user is not None

    response = client.post(
        "/auth/login",
        data={"username": "supernastya", "password": "hashedpassword"}
    )


    assert response.status_code == 200


    response_json = response.json()
    assert "access_token" in response_json


    assert response_json["token_type"] == "bearer"





