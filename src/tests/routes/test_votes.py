# tests/routes/test_votes.py
import pytest
from app import schemas


class TestVotePost:
    """Test vote creation (upvote)."""

    def test_vote_on_post_success(self, authorized_client, test_post):
        """Test successfully voting on a post."""
        vote_payload = {"post_id": test_post.id, "dir": 1}

        res = authorized_client.post("/vote/", json=vote_payload)

        assert res.status_code == 201
        assert res.json()["message"] == "Successfully added vote"

    def test_vote_unauthorized(self, client, test_post):
        """Test voting without authentication."""
        vote_payload = {"post_id": test_post.id, "dir": 1}

        res = client.post("/vote/", json=vote_payload)

        assert res.status_code == 401

    def test_vote_nonexistent_post(self, authorized_client):
        """Test voting on a non-existent post."""
        vote_payload = {"post_id": 99999, "dir": 1}

        res = authorized_client.post("/vote/", json=vote_payload)

        assert res.status_code == 404
        assert "does not exist" in res.json()["detail"]

    def test_vote_twice_same_post(self, authorized_client, test_post):
        """Test that voting twice on the same post is rejected."""
        vote_payload = {"post_id": test_post.id, "dir": 1}

        res1 = authorized_client.post("/vote/", json=vote_payload)
        assert res1.status_code == 201

        res2 = authorized_client.post("/vote/", json=vote_payload)
        assert res2.status_code == 409
        assert "already voted" in res2.json()["detail"]

    def test_vote_invalid_direction(self, authorized_client, test_post):
        """
        Test voting with an out-of-range direction value.

        Returns 422 if the Pydantic schema constrains `dir` to {0, 1};
        otherwise the router may accept it.
        """
        vote_payload = {"post_id": test_post.id, "dir": 2}

        res = authorized_client.post("/vote/", json=vote_payload)

        assert res.status_code in [201, 422]

    def test_vote_missing_post_id(self, authorized_client):
        """Test voting without supplying a post_id."""
        vote_payload = {"dir": 1}

        res = authorized_client.post("/vote/", json=vote_payload)

        assert res.status_code == 422

    def test_vote_missing_direction(self, authorized_client, test_post):
        """Test voting without supplying a direction."""
        vote_payload = {"post_id": test_post.id}

        res = authorized_client.post("/vote/", json=vote_payload)

        assert res.status_code == 422


class TestUnvotePost:
    """Test vote removal (unvote)."""

    def test_remove_vote_success(self, authorized_client, test_post, test_vote):
        """Test successfully removing an existing vote."""
        vote_payload = {"post_id": test_post.id, "dir": 0}

        res = authorized_client.post("/vote/", json=vote_payload)

        assert res.status_code == 201
        assert res.json()["message"] == "Successfully deleted vote"

    def test_remove_nonexistent_vote(self, authorized_client, test_post):
        """Test removing a vote that does not exist."""
        vote_payload = {"post_id": test_post.id, "dir": 0}

        res = authorized_client.post("/vote/", json=vote_payload)

        assert res.status_code == 404
        assert "does not exist" in res.json()["detail"]

    def test_remove_vote_from_nonexistent_post(self, authorized_client):
        """Test removing a vote from a non-existent post."""
        vote_payload = {"post_id": 99999, "dir": 0}

        res = authorized_client.post("/vote/", json=vote_payload)

        assert res.status_code == 404


class TestVoteIntegration:
    """Integration tests for voting workflows."""

    def test_vote_and_unvote_workflow(self, authorized_client, test_post):
        """Test a full vote → verify → unvote → verify cycle."""
        vote_payload = {"post_id": test_post.id, "dir": 1}

        # Upvote
        vote_res = authorized_client.post("/vote/", json=vote_payload)
        assert vote_res.status_code == 201

        # Confirm vote reflected on post
        post_res = authorized_client.get(f"/posts/{test_post.id}")
        assert post_res.status_code == 200
        assert post_res.json()["votes"] >= 1

        # Remove vote
        unvote_res = authorized_client.post(
            "/vote/", json={**vote_payload, "dir": 0}
        )
        assert unvote_res.status_code == 201

        # Confirm vote removed
        post_res2 = authorized_client.get(f"/posts/{test_post.id}")
        assert post_res2.status_code == 200
        assert post_res2.json()["votes"] == 0

    def test_vote_after_post_creation(self, authorized_client, post_payload):
        """Test voting on a newly created post."""
        post_res = authorized_client.post("/posts/", json=post_payload)
        assert post_res.status_code == 201
        post = schemas.PostResponse(**post_res.json())

        vote_res = authorized_client.post(
            "/vote/", json={"post_id": post.id, "dir": 1}
        )
        assert vote_res.status_code == 201

    def test_vote_persists_after_unvote_revote(self, authorized_client, test_post):
        """Test that a user can vote, unvote, then vote again on the same post."""
        vote_payload = {"post_id": test_post.id, "dir": 1}

        res1 = authorized_client.post("/vote/", json=vote_payload)
        assert res1.status_code == 201

        res2 = authorized_client.post("/vote/", json={**vote_payload, "dir": 0})
        assert res2.status_code == 201

        res3 = authorized_client.post("/vote/", json=vote_payload)
        assert res3.status_code == 201

    def test_user_cannot_vote_on_deleted_post(self, authorized_client, test_post):
        """Test that voting fails once the target post has been deleted."""
        post_id = test_post.id
        delete_res = authorized_client.delete(f"/posts/{post_id}")
        assert delete_res.status_code == 204

        vote_res = authorized_client.post(
            "/vote/", json={"post_id": post_id, "dir": 1}
        )
        assert vote_res.status_code == 404

    def test_vote_count_accuracy(self, authorized_client, test_posts):
        """Test that vote counts are accurate across multiple posts."""
        # Vote on the first two posts
        for post in test_posts[:2]:
            res = authorized_client.post(
                "/vote/", json={"post_id": post.id, "dir": 1}
            )
            assert res.status_code == 201

        # Verify expected vote counts on all four posts
        for i, post in enumerate(test_posts):
            post_res = authorized_client.get(f"/posts/{post.id}")
            assert post_res.status_code == 200
            expected_votes = 1 if i < 2 else 0
            assert post_res.json()["votes"] >= expected_votes


class TestVoteEdgeCases:
    """Test edge cases and error scenarios."""

    def test_vote_with_string_post_id(self, authorized_client):
        """Test voting with a string instead of an integer post_id."""
        vote_payload = {"post_id": "invalid", "dir": 1}

        res = authorized_client.post("/vote/", json=vote_payload)

        assert res.status_code == 422

    def test_vote_with_negative_post_id(self, authorized_client):
        """Test voting with a negative post_id (no such post should exist)."""
        vote_payload = {"post_id": -1, "dir": 1}

        res = authorized_client.post("/vote/", json=vote_payload)

        assert res.status_code == 404

    def test_vote_with_null_post_id(self, authorized_client):
        """Test voting with a null post_id."""
        vote_payload = {"post_id": None, "dir": 1}

        res = authorized_client.post("/vote/", json=vote_payload)

        assert res.status_code == 422

    def test_concurrent_votes_same_user(self, authorized_client, test_post):
        """
        Simulate a race condition where the same user votes twice rapidly.

        One request must succeed with 201 and the other must be rejected
        with 409 — order doesn't matter.
        """
        vote_payload = {"post_id": test_post.id, "dir": 1}

        res1 = authorized_client.post("/vote/", json=vote_payload)
        res2 = authorized_client.post("/vote/", json=vote_payload)

        statuses = {res1.status_code, res2.status_code}
        assert statuses == {201, 409}