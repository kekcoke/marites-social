# src/tests/conftest.py
import copy
import secrets
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models, utils
from app.auth import oauth2
from app.config import get_config
from app.core.enums import (
    AccountRole,
    AccountType,
    AttendeeStatus,
    IntegrationType,
    NotificationType,
    OrderStatus,
    PaymentMethod,
)
from app.db import Base, get_db_session
from app.main import app

fake = Faker()

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"

SQLALCHEMY_DB_URL = get_config().get_db_database_url()
engine = create_engine(SQLALCHEMY_DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Run migrations once for the full test session, then tear down."""
    alembic_cfg = Config(str(ALEMBIC_INI))
    alembic_cfg.set_main_option("sqlalchemy.url", SQLALCHEMY_DB_URL)
    command.upgrade(alembic_cfg, "head")
    yield
    command.downgrade(alembic_cfg, "base")


@pytest.fixture(scope="function")
def db_session():
    """
    Provide a transactional DB session per test.

    The connection wraps everything in a SAVEPOINT so that any commits made
    inside the app (or fixtures) are visible within the same connection but
    the outer transaction is rolled back at teardown, leaving the DB clean.
    """
    connection = engine.connect()
    transaction = connection.begin()
    # Use a nested (SAVEPOINT) transaction so that session.commit() inside
    # fixtures / route handlers doesn't actually commit to the DB.
    db = TestingSessionLocal(bind=connection)
    db.begin_nested()

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Test client whose DB dependency is wired to the *same* session used by
    all other fixtures in the test.  This ensures data created in fixtures is
    visible to the running application.
    """

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass  # rollback handled by db_session fixture

    app.dependency_overrides[get_db_session] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db_session, None)


# ============================================================================
# User fixtures
# ============================================================================


@pytest.fixture
def user_payload():
    """Generate a random valid user payload."""
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
    """Generate a second random valid user payload."""
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
    """Create a user directly in the database and return user + plain password."""
    hashed_password = utils.hash_password(user_payload["password"])
    new_user = models.User(
        username=user_payload["username"],
        email=user_payload["email"],
        hashed_password=hashed_password,
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    return {"user": new_user, "password": user_payload["password"]}


@pytest.fixture
def test_user_2(db_session, user_payload_2):
    """Create a second user directly in the database."""
    hashed_password = utils.hash_password(user_payload_2["password"])
    new_user = models.User(
        username=user_payload_2["username"],
        email=user_payload_2["email"],
        hashed_password=hashed_password,
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    return {"user": new_user, "password": user_payload_2["password"]}


@pytest.fixture
def access_token(test_user):
    """Generate a JWT access token for test_user."""
    token, _ = oauth2.create_access_token_and_expiry(
        data={"sub": str(test_user["user"].id)}
    )
    return token


@pytest.fixture
def access_token_2(test_user_2):
    """Generate a JWT access token for test_user_2."""
    token, _ = oauth2.create_access_token_and_expiry(
        data={"sub": str(test_user_2["user"].id)}
    )
    return token


@pytest.fixture
def authorized_client(client, access_token):
    """Test client pre-loaded with test_user's Bearer token."""
    auth_client = copy.copy(client)
    auth_client.headers = dict(client.headers)
    auth_client.headers["Authorization"] = f"Bearer {access_token}"
    return auth_client


@pytest.fixture
def authorized_client_2(client, access_token_2):
    """Test client pre-loaded with test_user_2's Bearer token."""
    auth_client = copy.copy(client)
    auth_client.headers = dict(client.headers)
    auth_client.headers["Authorization"] = f"Bearer {access_token_2}"
    return auth_client


# ============================================================================
# Post / Vote fixtures
# ============================================================================


@pytest.fixture
def post_payload():
    """Generate a random valid post creation payload."""
    return {
        "title": fake.sentence(nb_words=6),
        "content": fake.paragraph(nb_sentences=5),
        "author": f"{fake.first_name()} {fake.last_name()}",
        "published": True,
    }


@pytest.fixture
def test_post(db_session, test_user):
    """Create a single post owned by test_user."""
    post = models.Post(
        title="Test Post",
        content="Test Content",
        author="Test Author",
        published=True,
        user_id=test_user["user"].id,
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post


@pytest.fixture
def test_posts(db_session, test_user, test_user_2):
    """Create four posts split between test_user and test_user_2."""
    posts_data = [
        {
            "title": "First post",
            "content": "First content",
            "author": "Author One",
            "published": True,
            "user_id": test_user["user"].id,
        },
        {
            "title": "Second post",
            "content": "Second content",
            "author": "Author One",
            "published": True,
            "user_id": test_user["user"].id,
        },
        {
            "title": "Third post",
            "content": "Third content",
            "author": "Author Two",
            "published": True,
            "user_id": test_user_2["user"].id,
        },
        {
            "title": "Fourth post",
            "content": "Fourth content",
            "author": "Author Two",
            "published": True,
            "user_id": test_user_2["user"].id,
        },
    ]
    posts = [models.Post(**data) for data in posts_data]
    db_session.add_all(posts)
    db_session.commit()
    for post in posts:
        db_session.refresh(post)
    return posts


@pytest.fixture
def test_vote(db_session, test_post, test_user):
    """Create a vote by test_user on test_post."""
    vote = models.Vote(
        post_id=test_post.id,
        user_id=test_user["user"].id,
    )
    db_session.add(vote)
    db_session.commit()
    db_session.refresh(vote)
    return vote