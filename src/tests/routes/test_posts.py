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
    