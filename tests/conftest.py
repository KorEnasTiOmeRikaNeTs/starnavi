# tests/conftest.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



from main import app
from models import Users
from database import get_db, Base

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(setup_database):
    try:
        yield TestingSessionLocal()
    finally:
        pass


@pytest.fixture
def create_test_user(db):
    existing_user = db.query(Users).filter(Users.email == "anastas@gmain.com").first()
    if existing_user:
        return existing_user

    user = Users(
        username="supernastya",
        email="anastas@gmain.com",
        hashed_password="hashedpassword",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def setup_database():
    # Скидаємо таблиці
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)



