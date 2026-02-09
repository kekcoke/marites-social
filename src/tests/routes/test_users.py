import faker
import random
from app import schemas

fake = faker.Faker()

def test_create_user():
    fname = fake.first_name()
    lname = fake.last_name()
    username = f"{fname}.{lname}"
    email = f"{username}@email.com"
    password = fake.password()
    res = client.post("/users/", json={
        "username": username,
        "email" : email,
        "password" : password
    })
    new_user = schemas.UserResponse(**res.json())
    assert new_user.email == email
    assert res.status_code == 201