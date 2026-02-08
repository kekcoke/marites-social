import faker
import random
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
fake = faker.Faker()

def test_create_user():
    password = fake.password()
    res = client.post("/users", json={
        "email": f"{fake.first_name()}.{fake.last_name()}@email.com",
        "password" : password
    })
    assert res.status_code == 201

    