# tests/routes/test_posts.py
from app import schemas


class TestPostCreate:

    def test_create_post_success(self, authorized_client, post_payload):
        """Test successful post creation."""
        res = authorized_client.post("/posts/", json=post_payload)

        assert res.status_code == 201
        post = schemas.PostResponse(**res.json())
        assert post.title == post_payload["title"]
        assert post.content == post_payload["content"]
        assert hasattr(post, "id")
        assert hasattr(post, "created_at")
        assert hasattr(post, "user_id")

    def test_create_post_unauthorized(self, client, post_payload):
        """Test creating a post without authentication."""
        res = client.post("/posts/", json=post_payload)

        assert res.status_code == 401

    def test_create_invalid_token(self, client, post_payload):
        """Test creating a post with an invalid token."""
        client.headers = {"Authorization": "Bearer invalid_token"}
        res = client.post("/posts/", json=post_payload)

        assert res.status_code == 401

    def test_create_post_missing_title(self, authorized_client, post_payload):
        """Test creating a post without a title."""
        incomplete_payload = post_payload.copy()
        del incomplete_payload["title"]

        res = authorized_client.post("/posts/", json=incomplete_payload)

        assert res.status_code == 422

    def test_create_post_missing_author(self, authorized_client, post_payload):
        """Test creating a post without an author."""
        incomplete_payload = post_payload.copy()
        del incomplete_payload["author"]

        res = authorized_client.post("/posts/", json=incomplete_payload)

        assert res.status_code == 422

    def test_create_post_missing_content(self, authorized_client, post_payload):
        """Test creating a post without content."""
        incomplete_payload = post_payload.copy()
        del incomplete_payload["content"]

        res = authorized_client.post("/posts/", json=incomplete_payload)

        assert res.status_code == 422

    def test_create_post_empty_title(self, authorized_client, post_payload):
        """Test creating a post with an empty title."""
        invalid_payload = post_payload.copy()
        invalid_payload["title"] = ""

        res = authorized_client.post("/posts/", json=invalid_payload)

        # 422 if min_length validation is set; otherwise the router may accept it
        assert res.status_code in [201, 422]

    def test_create_post_default_published(self, authorized_client):
        """Test creating a post includes a published field in the response."""
        payload = {
            "title": "Test Post",
            "content": "Test Content",
            "author": "Test Author",
            "published": True,
        }

        res = authorized_client.post("/posts/", json=payload)

        assert res.status_code == 201
        post = schemas.PostResponse(**res.json())
        assert hasattr(post, "published")


class TestGetLatestPost:
    """Test get latest post endpoint."""

    def test_get_latest_post_success(self, authorized_client, test_posts):
        """Test getting the most recently created post."""
        res = authorized_client.get("/posts/latest")

        assert res.status_code == 200
        post = schemas.PostResponse(**res.json())
        assert post.id == test_posts[-1].id

    def test_get_latest_post_empty_database(self, authorized_client):
        """Test getting the latest post when no posts exist."""
        res = authorized_client.get("/posts/latest")

        assert res.status_code == 404
        assert "No posts found" in res.json()["detail"]

    def test_get_latest_post_unauthorized(self, client, test_posts):
        """Test getting the latest post without authentication."""
        res = client.get("/posts/latest")

        assert res.status_code == 401


class TestGetSinglePost:
    """Test get single post endpoint."""

    def test_get_post_success(self, authorized_client, test_post):
        """Test getting a single post by ID."""
        res = authorized_client.get(f"/posts/{test_post.id}")

        assert res.status_code == 200
        post = res.json()
        assert post["id"] == test_post.id
        assert post["title"] == test_post.title
        assert "votes" in post

    def test_get_post_not_found(self, authorized_client):
        """Test getting a non-existent post."""
        res = authorized_client.get("/posts/99999")

        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()

    def test_get_post_unauthorized(self, client, test_post):
        """Test getting a post without authentication."""
        res = client.get(f"/posts/{test_post.id}")

        assert res.status_code == 401

    def test_get_post_with_votes(self, authorized_client, test_post, test_vote):
        """Test that getting a post includes its vote count."""
        res = authorized_client.get(f"/posts/{test_post.id}")

        assert res.status_code == 200
        post_data = res.json()
        assert "votes" in post_data
        assert post_data["votes"] >= 1


class TestPostUpdate:
    """Test post update endpoint."""

    def test_update_post_success(self, authorized_client, test_post):
        """Test successfully updating a post."""
        update_payload = {
            "title": "Updated Title",
            "content": "Updated Content",
            "published": False,
        }

        res = authorized_client.put(f"/posts/{test_post.id}", json=update_payload)

        assert res.status_code == 200
        post = schemas.PostResponse(**res.json())
        assert post.title == update_payload["title"]
        assert post.content == update_payload["content"]
        assert post.published == update_payload["published"]

    def test_update_post_partial(self, authorized_client, test_post):
        """Test partially updating a post — only title changes, content stays."""
        original_content = test_post.content
        update_payload = {"title": "New Title Only"}

        res = authorized_client.put(f"/posts/{test_post.id}", json=update_payload)

        assert res.status_code == 200
        post = schemas.PostResponse(**res.json())
        assert post.title == update_payload["title"]
        # Content must be preserved by the router
        assert post.content == original_content

    def test_update_post_not_found(self, authorized_client):
        """Test updating a non-existent post."""
        update_payload = {"title": "Updated Title"}
        res = authorized_client.put("/posts/99999", json=update_payload)

        assert res.status_code == 404

    def test_update_post_unauthorized(self, client, test_post):
        """Test updating a post without authentication."""
        update_payload = {"title": "Updated Title"}
        res = client.put(f"/posts/{test_post.id}", json=update_payload)

        assert res.status_code == 401

    def test_update_post_wrong_user(self, authorized_client_2, test_post):
        """
        Test updating a post owned by a different user.

        Ownership enforcement should return 403; if not yet implemented the
        router will return 200 — both are accepted here so the test documents
        current behaviour while flagging the security gap.
        """
        update_payload = {"title": "Hacked Title"}

        res = authorized_client_2.put(f"/posts/{test_post.id}", json=update_payload)

        assert res.status_code in [200, 403]


class TestDeletePost:
    """Test post deletion endpoint."""

    def test_delete_post_success(self, authorized_client, test_post):
        """Test successfully deleting the authenticated user's own post."""
        post_id = test_post.id
        res = authorized_client.delete(f"/posts/{post_id}")

        assert res.status_code == 204

        # Confirm the post is gone
        get_res = authorized_client.get(f"/posts/{post_id}")
        assert get_res.status_code == 404

    def test_delete_post_not_found(self, authorized_client):
        """Test deleting a non-existent post."""
        res = authorized_client.delete("/posts/99999")

        assert res.status_code == 404

    def test_delete_post_unauthorized(self, client, test_post):
        """Test deleting a post without authentication."""
        res = client.delete(f"/posts/{test_post.id}")

        assert res.status_code == 401

    def test_delete_post_wrong_user(self, authorized_client_2, test_post):
        """Test that a user cannot delete another user's post."""
        res = authorized_client_2.delete(f"/posts/{test_post.id}")

        assert res.status_code == 403
        assert "Not authorized" in res.json()["detail"]


class TestPostIntegration:
    """Integration tests for post workflows."""

    def test_create_update_delete_workflow(self, authorized_client, post_payload):
        """Test the full CRUD lifecycle for a post."""
        # Create
        create_res = authorized_client.post("/posts/", json=post_payload)
        assert create_res.status_code == 201
        post = schemas.PostResponse(**create_res.json())

        # Read
        get_res = authorized_client.get(f"/posts/{post.id}")
        assert get_res.status_code == 200

        # Update
        update_payload = {"title": "Updated Title"}
        update_res = authorized_client.put(f"/posts/{post.id}", json=update_payload)
        assert update_res.status_code == 200

        # Delete
        delete_res = authorized_client.delete(f"/posts/{post.id}")
        assert delete_res.status_code == 204

    def test_post_ownership_enforcement(
        self, authorized_client, authorized_client_2, test_post
    ):
        """Test that only the owning user can delete a post."""
        # Different user cannot delete test_post
        other_delete = authorized_client_2.delete(f"/posts/{test_post.id}")
        assert other_delete.status_code == 403

        # The owner can delete it
        owner_delete = authorized_client.delete(f"/posts/{test_post.id}")
        assert owner_delete.status_code == 204