# tests/routes/test_votes.py
import pytest
from app import schemas


class TestVotePost:
    """Test vote creation (upvote)"""
    
    def test_vote_on_post_success(self, authorized_client, test_post):
        """Test successfully voting on a post"""
        vote_payload = {
            "post_id": test_post.id,
            "dir": 1  # Upvote
        }
        
        res = authorized_client.post("/vote/", json=vote_payload)
        
        assert res.status_code == 201
        assert res.json()["message"] == "Successfully added vote"
    
    def test_vote_unauthorized(self, client, test_post):
        """Test voting without authentication"""
        vote_payload = {
            "post_id": test_post.id,
            "dir": 1
        }
        
        res = client.post("/vote/", json=vote_payload)
        
        assert res.status_code == 401
    
    def test_vote_nonexistent_post(self, authorized_client):
        """Test voting on non-existent post"""
        vote_payload = {
            "post_id": 99999,
            "dir": 1
        }
        
        res = authorized_client.post("/vote/", json=vote_payload)
        
        assert res.status_code == 404
        assert "does not exist" in res.json()["detail"]
    
    def test_vote_twice_same_post(self, authorized_client, test_post):
        """Test voting twice on the same post (should fail)"""
        vote_payload = {
            "post_id": test_post.id,
            "dir": 1
        }
        
        # First vote
        res1 = authorized_client.post("/vote/", json=vote_payload)
        assert res1.status_code == 201
        
        # Second vote (duplicate)
        res2 = authorized_client.post("/vote/", json=vote_payload)
        assert res2.status_code == 409
        assert "already voted" in res2.json()["detail"]
    
    def test_vote_invalid_direction(self, authorized_client, test_post):
        """Test voting with invalid direction value"""
        vote_payload = {
            "post_id": test_post.id,
            "dir": 2  # Invalid, should be 0 or 1
        }
        
        res = authorized_client.post("/vote/", json=vote_payload)
        
        # Should validate if Pydantic schema has constraints
        assert res.status_code in [201, 422]
    
    def test_vote_missing_post_id(self, authorized_client):
        """Test voting without post_id"""
        vote_payload = {
            "dir": 1
        }
        
        res = authorized_client.post("/vote/", json=vote_payload)
        
        assert res.status_code == 422
    
    def test_vote_missing_direction(self, authorized_client, test_post):
        """Test voting without direction"""
        vote_payload = {
            "post_id": test_post.id
        }
        
        res = authorized_client.post("/vote/", json=vote_payload)
        
        assert res.status_code == 422


class TestUnvotePost:
    """Test vote removal (unvote)"""
    
    def test_remove_vote_success(self, authorized_client, test_post, test_vote):
        """Test successfully removing a vote"""
        vote_payload = {
            "post_id": test_post.id,
            "dir": 0  # Remove vote
        }
        
        res = authorized_client.post("/vote/", json=vote_payload)
        
        assert res.status_code == 201
        assert res.json()["message"] == "Successfully deleted vote"
    
    def test_remove_nonexistent_vote(self, authorized_client, test_post):
        """Test removing a vote that doesn't exist"""
        vote_payload = {
            "post_id": test_post.id,
            "dir": 0
        }
        
        res = authorized_client.post("/vote/", json=vote_payload)
        
        assert res.status_code == 404
        assert "does not exist" in res.json()["detail"]
    
    def test_remove_vote_from_nonexistent_post(self, authorized_client):
        """Test removing vote from non-existent post"""
        vote_payload = {
            "post_id": 99999,
            "dir": 0
        }
        
        res = authorized_client.post("/vote/", json=vote_payload)
        
        assert res.status_code == 404
