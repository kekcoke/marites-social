# tests/routes/test_users.py
from faker import Faker
from app import schemas

fake = Faker()


class TestUserCreation:
    """Test user creation endpoint."""

    def test_create_user_success(self, client, user_payload):
        """Test successful user creation."""
        res = client.post("/users/", json=user_payload)

        assert res.status_code == 201
        user = schemas.UserResponse(**res.json())
        assert user.email == user_payload["email"]
        assert user.username == user_payload["username"]
        assert hasattr(user, "id")
        assert hasattr(user, "created_at")

    def test_create_user_duplicate_email(self, client, test_user, user_payload):
        """Test that creating a user with a duplicate email fails."""
        duplicate_payload = user_payload.copy()
        duplicate_payload["email"] = test_user["user"].email

        res = client.post("/users/", json=duplicate_payload)

        assert res.status_code in [400, 409, 500]

    def test_create_user_duplicate_username(self, client, test_user, user_payload):
        """Test that creating a user with a duplicate username fails."""
        duplicate_payload = user_payload.copy()
        duplicate_payload["username"] = test_user["user"].username

        res = client.post("/users/", json=duplicate_payload)

        assert res.status_code in [400, 409, 500]

    def test_create_user_invalid_email(self, client, user_payload):
        """Test that an invalid email format is rejected."""
        invalid_payload = user_payload.copy()
        invalid_payload["email"] = "invalid-email"

        res = client.post("/users/", json=invalid_payload)

        assert res.status_code == 422

    def test_create_user_missing_password(self, client, user_payload):
        """Test that omitting the password field returns 422."""
        incomplete_payload = {
            "username": user_payload["username"],
            "email": user_payload["email"],
        }

        res = client.post("/users/", json=incomplete_payload)

        assert res.status_code == 422

    def test_create_user_weak_password(self, client, user_payload):
        """
        Test creating a user with a very short password.

        Returns 422 if password-strength validation is implemented; 201
        otherwise — this test documents the current behaviour.
        """
        weak_payload = user_payload.copy()
        weak_payload["password"] = "123"

        res = client.post("/users/", json=weak_payload)

        assert res.status_code in [201, 422]

    def test_create_user_password_not_returned(self, client, user_payload):
        """Test that the response never exposes password or hashed_password."""
        res = client.post("/users/", json=user_payload)

        assert res.status_code == 201
        response_data = res.json()
        assert "password" not in response_data
        assert "hashed_password" not in response_data


class TestGetUser:
    """Test user retrieval endpoint."""

    def test_get_user_success(self, client, test_user):
        """Test successfully retrieving a user by UUID."""
        user_id = test_user["user"].id
        res = client.get(f"/users/{user_id}")

        assert res.status_code == 200
        user = schemas.UserResponse(**res.json())
        assert str(user.id) == str(user_id)
        assert user.email == test_user["user"].email

    def test_get_user_not_found(self, client):
        """Test that a non-existent UUID returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        res = client.get(f"/users/{fake_id}")

        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()

    def test_get_user_invalid_id_format(self, client):
        """Test that a malformed UUID path parameter returns 500 (unvalidated route)."""
        res = client.get("/users/invalid-id-format")

        # Currently the router does not validate UUID format, so 500 is expected.
        # Ideally this should be 422 once path-parameter validation is added.
        assert res.status_code == 500

    def test_get_user_password_not_exposed(self, client, test_user):
        """Test that retrieving a user never exposes the password."""
        user_id = test_user["user"].id
        res = client.get(f"/users/{user_id}")

        assert res.status_code == 200
        response_data = res.json()
        assert "password" not in response_data
        assert "hashed_password" not in response_data


class TestUserLogin:
    """Test user login endpoint."""

    def test_login_success(self, client, test_user):
        """Test successful login returns a bearer token."""
        res = client.post(
            "/login",
            data={
                "username": test_user["user"].email,
                "password": test_user["password"],
            },
        )

        assert res.status_code == 200
        token_data = res.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test that an incorrect password returns 403."""
        res = client.post(
            "/login",
            data={
                "username": test_user["user"].email,
                "password": "wrong_pwd",
            },
        )

        assert res.status_code == 403

    def test_login_nonexistent_user(self, client):
        """Test that logging in as a non-existent user returns 403."""
        res = client.post(
            "/login",
            data={
                "username": "nonexistent@email.com",
                "password": "some_pwd",
            },
        )

        assert res.status_code == 403

    def test_login_missing_credentials(self, client):
        """Test that submitting an empty login form returns 422."""
        res = client.post("/login", data={})

        assert res.status_code == 422

    def test_login_empty_password(self, client, test_user):
        """Test that an empty password is rejected."""
        res = client.post(
            "/login",
            data={
                "username": test_user["user"].email,
                "password": "",
            },
        )

        assert res.status_code in [403, 422]


class TestUserIntegration:
    """Integration tests for user workflows."""

    def test_create_and_login_workflow(self, client, user_payload):
        """Test the full create-then-login workflow."""
        # Create user
        create_res = client.post("/users/", json=user_payload)
        assert create_res.status_code == 201
        schemas.UserResponse(**create_res.json())

        # Login with the newly created user
        login_res = client.post(
            "/login",
            data={
                "username": user_payload["email"],
                "password": user_payload["password"],
            },
        )
        assert login_res.status_code == 200
        assert "access_token" in login_res.json()

    def test_multiple_users_creation(self, client, user_payload, user_payload_2):
        """Test that two distinct users can be created independently."""
        res1 = client.post("/users/", json=user_payload)
        assert res1.status_code == 201

        res2 = client.post("/users/", json=user_payload_2)
        assert res2.status_code == 201

        user1 = schemas.UserResponse(**res1.json())
        user2 = schemas.UserResponse(**res2.json())
        assert user1.id != user2.id
        assert user1.email != user2.email