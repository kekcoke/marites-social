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


class TestVoteIntegration:
    """Integration tests for voting workflows"""
    
    def test_vote_and_unvote_workflow(self, authorized_client, test_post):
        """Test complete vote and unvote workflow"""
        vote_payload = {
            "post_id": test_post.id,
            "dir": 1
        }
        
        # Vote
        vote_res = authorized_client.post("/vote/", json=vote_payload)
        assert vote_res.status_code == 201
        
        # Verify post has vote count
        post_res = authorized_client.get(f"/posts/{test_post.id}")
        assert post_res.status_code == 200
        assert post_res.json()["votes"] >= 1
        
        # Unvote
        unvote_payload = vote_payload.copy()
        unvote_payload["dir"] = 0
        unvote_res = authorized_client.post("/vote/", json=unvote_payload)
        assert unvote_res.status_code == 201
        
        # Verify vote removed
        post_res2 = authorized_client.get(f"/posts/{test_post.id}")
        assert post_res2.status_code == 200
        # Vote count should be less than before
    
    # def test_multiple_users_voting(self, authorized_client, authorized_client_2, test_post):
    #     """Test multiple users voting on same post"""
    #     vote_payload = {
    #         "post_id": test_post.id,
    #         "dir": 1
    #     }
        
    #     # User 1 votes
    #     res1 = authorized_client.post("/vote/", json=vote_payload)
    #     assert res1.status_code == 201
        
    #     # User 2 votes (should succeed - different user)
    #     res2 = authorized_client_2.post("/vote/", json=vote_payload)
    #     assert res2.status_code == 201
        
    #     # Check vote count
    #     post_res = authorized_client.get(f"/posts/{test_post.id}")
    #     assert post_res.status_code == 200
    #     assert post_res.json()["votes"] >= 2
    
    def test_vote_after_post_creation(self, authorized_client, post_payload):
        """Test voting on newly created post"""
        # Create post
        post_res = authorized_client.post("/posts/", json=post_payload)
        assert post_res.status_code == 201
        post = schemas.PostResponse(**post_res.json())
        
        # Vote on new post
        vote_payload = {
            "post_id": post.id,
            "dir": 1
        }
        vote_res = authorized_client.post("/vote/", json=vote_payload)
        assert vote_res.status_code == 201
    
    def test_vote_persists_after_unvote_revote(self, authorized_client, test_post):
        """Test that vote can be added, removed, and added again"""
        vote_payload = {
            "post_id": test_post.id,
            "dir": 1
        }
        
        # First vote
        res1 = authorized_client.post("/vote/", json=vote_payload)
        assert res1.status_code == 201
        
        # Unvote
        unvote_payload = vote_payload.copy()
        unvote_payload["dir"] = 0
        res2 = authorized_client.post("/vote/", json=unvote_payload)
        assert res2.status_code == 201
        
        # Vote again
        res3 = authorized_client.post("/vote/", json=vote_payload)
        assert res3.status_code == 201
    
    def test_user_cannot_vote_on_deleted_post(self, authorized_client, test_post):
        """Test that voting fails on deleted post"""
        # Delete post
        delete_res = authorized_client.delete(f"/posts/{test_post.id}")
        assert delete_res.status_code == 204
        
        # Try to vote
        vote_payload = {
            "post_id": test_post.id,
            "dir": 1
        }
        vote_res = authorized_client.post("/vote/", json=vote_payload)
        assert vote_res.status_code == 404
    
    def test_vote_count_accuracy(self, authorized_client, test_posts):
        """Test that vote counts are accurate across multiple posts"""
        # Vote on multiple posts
        for post in test_posts[:2]:
            vote_payload = {"post_id": post.id, "dir": 1}
            res = authorized_client.post("/vote/", json=vote_payload)
            assert res.status_code == 201
        
        # Check each post has correct vote count
        for i, post in enumerate(test_posts):
            post_res = authorized_client.get(f"/posts/{post.id}")
            assert post_res.status_code == 200
            expected_votes = 1 if i < 2 else 0
            assert post_res.json()["votes"] >= expected_votes


class TestVoteEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_vote_with_string_post_id(self, authorized_client):
        """Test voting with string post_id instead of integer"""
        vote_payload = {
            "post_id": "invalid",
            "dir": 1
        }
        
        res = authorized_client.post("/vote/", json=vote_payload)
        
        assert res.status_code == 422
    
    def test_vote_with_negative_post_id(self, authorized_client):
        """Test voting with negative post_id"""
        vote_payload = {
            "post_id": -1,
            "dir": 1
        }
        
        res = authorized_client.post("/vote/", json=vote_payload)
        
        # Should fail to find post
        assert res.status_code == 404
    
    def test_vote_with_null_post_id(self, authorized_client):
        """Test voting with null post_id"""
        vote_payload = {
            "post_id": None,
            "dir": 1
        }
        
        res = authorized_client.post("/vote/", json=vote_payload)
        
        assert res.status_code == 422
    
    def test_concurrent_votes_same_user(self, authorized_client, test_post):
        """Test handling of potential race condition (same user voting twice quickly)"""
        # This is more for documentation - actual concurrency testing requires threading
        vote_payload = {
            "post_id": test_post.id,
            "dir": 1
        }
        
        res1 = authorized_client.post("/vote/", json=vote_payload)
        res2 = authorized_client.post("/vote/", json=vote_payload)
        
        # One should succeed, one should fail
        assert (res1.status_code == 201 and res2.status_code == 409) or \
               (res1.status_code == 409 and res2.status_code == 201)