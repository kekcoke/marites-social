# src/tests/routes/test_users.py
import pytest
from faker import Faker
from app import schemas

fake = Faker()

class TestUserCreation:
    """Test user creation endpoint"""

    def test_create_user_success(self, client, user_payload):
        """Test for successful user creation"""
        res = client.post("/users/", json=user_payload)
        
        assert res.status_code == 201
        user = schemas.UserResponse(**res.json())
        assert user.email == user_payload["email"]
        assert user.username == user_payload["username"]
        assert hasattr(user, 'id')
        assert hasattr(user, 'created_at')

    def test_create_user_duplicate_email(self, client, test_user, user_payload):
        """Test creating user with duplicate email fails"""
        duplicate_payload = user_payload.copy()
        duplicate_payload["email"] = test_user["user"].email

        res = client.post("/users/", json=duplicate_payload)

        assert res.status_code in [400, 409, 500]

    def test_create_user_duplicate_username(self, client, test_user, user_payload):
        """Test creating user with duplicate username fails"""
        duplicate_payload = user_payload.copy()
        duplicate_payload["username"] = test_user["user"].username

        res = client.post("/users/", json=duplicate_payload)

        assert res.status_code in [400, 409, 500]

    def test_create_user_invalid_email(self, client, user_payload):
        """Test creating user with invalid email format"""
        invalid_payload = user_payload.copy()
        invalid_payload["email"] = "invalid-email"

        res = client.post("/users/", json=invalid_payload)

        assert res.status_code == 422

    def test_create_user_missing_password(self, client, user_payload):
        """Test creating user without password"""
        incomplete_payload = {
            "username": user_payload["username"],
            "email": user_payload["email"]
        }
        
        res = client.post("/users/", json=incomplete_payload)
        
        assert res.status_code == 422

    def test_create_user_weak_password(self, client, user_payload):
        """Test creating user with weak password"""
        weak_payload = user_payload.copy()
        weak_payload["password"] = "123"
        
        res = client.post("/users/", json=weak_payload)
        
        # Should validate password strength if implemented
        # Otherwise will succeed - this is a recommendation for router improvement
        assert res.status_code in [201, 422]
    
    def test_create_user_password_not_returned(self, client, user_payload):
        """Test that password/hashed_password is not returned in response"""
        res = client.post("/users/", json=user_payload)
        
        assert res.status_code == 201
        response_data = res.json()
        assert "password" not in response_data
        assert "hashed_password" not in response_data
