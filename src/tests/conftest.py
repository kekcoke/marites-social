# src/tests/config_test.py
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from faker import Faker
from fastapi.testclient import TestClient

from app.main import app
from app.db import Base, get_db_session
from app.config import get_config
from app import models, schemas, utils
from app.auth import oauth2

fake = Faker()

# Test db setup
SQLALCHEMY_DB_URL = f'{get_config().db_database_url}_test'
engine = create_engine(SQLALCHEMY_DB_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

def override_get_db_test():
    """Override db dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    # Replace db with test on app
    app.dependency_overrides[get_db_session] = override_get_db_test
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh db session for each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    
@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with fresh db"""
    with TestClient(app) as c:
        yield c

# User fixtures
@pytest.fixture
def user_payload():
    """Generate random user payload"""
    fname = fake.first_name()
    lname = fake.last_name()
    username = f"{fname}.{lname}".lower()
    
    return {
        "username": username,
        "email": f"{username}@email.com",
        "password": fake.password(length=12),
    }

@pytest.fixture
def user_payload_2():
    """Generate second user payload for multi-user tests"""
    fname = fake.first_name()
    lname = fake.last_name()
    username = f"{fname}.{lname}".lower()
    
    return {
        "username": username,
        "email": f"{username}@email.com",
        "password": fake.password(length=12),
    }

@pytest.fixture
def test_user(db_session, user_payload):
    """Create a user directly in database"""
    hashed_password = utils.hash_password(user_payload["password"])
    new_user = models.User(
        username=user_payload["username"],
        email=user_payload["email"],
        hashed_password=hashed_password
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    
    return {
        "user": new_user,
        "password": user_payload["password"]
    }


@pytest.fixture
def test_user_2(db_session, user_payload_2):
    """Create a second user for multi-user tests"""
    hashed_password = utils.hash_password(user_payload_2["password"])
    new_user = models.User(
        username=user_payload_2["username"],
        email=user_payload_2["email"],
        hashed_password=hashed_password
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    
    return {
        "user": new_user,
        "password": user_payload_2["password"]
    }

@pytest.fixture
def token(test_user):
    """Generate access token for test user"""
    access_token = oauth2.create_access_token(
        data={"user_id": str(test_user["user"].id)}
    )
    return access_token

@pytest.fixture
def token_2(test_user_2):
    """Generate access token for second test user"""
    access_token = oauth2.create_access_token(
        data={"user_id": str(test_user_2["user"].id)}
    )
    return access_token


