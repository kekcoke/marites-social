import pytest
from fastapi.testclient import TestClient
from app.db import get_db_session, Base
from app.config import get_config
from app.main import app
from app import schemas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DB_URL = f'{get_config().db_database_url}_test'

engine = create_engine(SQLALCHEMY_DB_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db_test():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Replace db with test on app
app.dependencies_overrides[get_db_session] = override_get_db_test()

@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)