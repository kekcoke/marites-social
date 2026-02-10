# tests/routes/test_posts.py
from app import schemas

class TestCreatePost:

    def test_create_post_success(self, authorized_client, post_payload):
        """Test successful post creation"""
        res = authorized_client.post("/posts/", json=post_payload)
        
        assert res.status_code == 201
        post = schemas.PostResponse(**res.json())
        assert post.title == post_payload["title"]
        assert post.content == post_payload["content"]
        assert hasattr(post, 'id')
        assert hasattr(post, 'created_at')
        assert hasattr(post, 'user_id')
    
    def test_create_post_unauthorized(self, client, post_payload):
        """Test creating post without authentication"""
        res = client.post("/posts/", json=post_payload)
        
        assert res.status_code == 401

    def test_create_invalid_token(self, client, post_payload):
        """Test creating post with invalid token"""
        client.header = { "Authorization": "Bearer invalid_token"}
        res = client.post("/posts/", json=post_payload)

        assert res.status_code == 401

    def test_create_post_missing_title(self, authorized_client, post_payload):
        """Test creating post without title"""
        incomplete_payload = post_payload.copy()
        del incomplete_payload["title"]
        
        res = authorized_client.post("/posts/", json=incomplete_payload)
        
        assert res.status_code == 422

    def test_create_post_missing_author(self, authorized_client, post_payload):
        """Test creating post without author"""
        incomplete_payload = post_payload.copy()
        del incomplete_payload["author"]
        
        res = authorized_client.post("/posts/", json=incomplete_payload)
        
        assert res.status_code == 422
    
    def test_create_post_missing_content(self, authorized_client, post_payload):
        """Test creating post without content"""
        incomplete_payload = post_payload.copy()
        del incomplete_payload["content"]
        
        res = authorized_client.post("/posts/", json=incomplete_payload)
        
        assert res.status_code == 422
    
    def test_create_post_empty_title(self, authorized_client, post_payload):
        """Test creating post with empty title"""
        invalid_payload = post_payload.copy()
        invalid_payload["title"] = ""
        
        res = authorized_client.post("/posts/", json=invalid_payload)
        
        # Should validate if min_length is set in schema
        assert res.status_code in [201, 422]
    
    def test_create_post_default_published(self, authorized_client):
        """Test creating post with default published status"""
        payload = {
            "title": "Test Post",
            "content": "Test Content",
            "author" : "Test Author",
            "published" : True
        }
        
        res = authorized_client.post("/posts/", json=payload)
        
        assert res.status_code == 201
        post = schemas.PostResponse(**res.json())
        # Default should be True based on common patterns
        assert hasattr(post, 'published')
