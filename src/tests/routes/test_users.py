# src/tests/routes/test_users.py
import pytest
from faker import Faker
from app import schemas

fake = Faker()

@pytest.fixture
def user_payload():
    fname = fake.first_name()
    lname = fake.last_name()
    username = f"{fname}.{lname}"

    return {
        "username": username,
        "email": f"{username}@email.com",
        "password" : fake.password(),
    }

@pytest.fixture
def created_user(client, user_payload):
    res = client.post("/users/", json=user_payload)

    assert res.status_code == 201

    user = schemas.UserResponse(**res.json())

    return {
        "user": user,
        "password" : user_payload["password"],
    }

def test_create_user(created_user):
    user = created_user["user"]
    assert user.email is not None


def test_login_user(client, created_user):
    res = client.post(
        "/login",
        data={
            "username": created_user["user"].email,
            "password": created_user["password"],
        },
    )

    assert res.status_code == 200