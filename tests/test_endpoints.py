"""
Tests for FastAPI endpoints
"""

import pytest


class TestGetRoot:
    """Test GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Test that root redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert len(activities) == 9
        
        # Verify structure of an activity
        assert "Chess Club" in activities
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_returns_correct_data(self, client):
        """Test that activities contain expected data"""
        response = client.get("/activities")
        activities = response.json()
        
        # Verify Chess Club data
        chess_club = activities["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Test POST /activities/{activity_name}/signup endpoint"""

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup successfully adds a participant"""
        response = client.post(
            "/activities/Basketball Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up newstudent@mergington.edu" in response.json()["message"]

        # Verify participant was added
        activities_response = client.get("/activities")
        basketball_team = activities_response.json()["Basketball Team"]
        assert "newstudent@mergington.edu" in basketball_team["participants"]

    def test_signup_updates_participant_count(self, client):
        """Test that signup updates the participant count"""
        # Basketball Team starts with 0 participants
        activities_response = client.get("/activities")
        basketball = activities_response.json()["Basketball Team"]
        initial_count = len(basketball["participants"])

        # Add a participant
        client.post("/activities/Basketball Team/signup?email=test@mergington.edu")

        # Verify count increased
        activities_response = client.get("/activities")
        basketball = activities_response.json()["Basketball Team"]
        assert len(basketball["participants"]) == initial_count + 1


class TestUnregisterFromActivity:
    """Test DELETE /activities/{activity_name}/signup endpoint"""

    def test_delete_removes_participant_from_activity(self, client):
        """Test that delete successfully removes a participant"""
        # First add a participant
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")

        # Then remove them
        response = client.delete(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Unregistered newstudent@mergington.edu" in response.json()["message"]

        # Verify participant was removed
        activities_response = client.get("/activities")
        chess_club = activities_response.json()["Chess Club"]
        assert "newstudent@mergington.edu" not in chess_club["participants"]

    def test_delete_updates_participant_count(self, client):
        """Test that delete updates the participant count"""
        # Add a participant first
        client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        
        # Get count after signup
        activities_response = client.get("/activities")
        chess_club = activities_response.json()["Chess Club"]
        count_after_signup = len(chess_club["participants"])

        # Delete the participant
        client.delete("/activities/Chess Club/signup?email=test@mergington.edu")

        # Verify count decreased
        activities_response = client.get("/activities")
        chess_club = activities_response.json()["Chess Club"]
        assert len(chess_club["participants"]) == count_after_signup - 1
