"""
Tests for the Activities API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

# Create test client
client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    original_activities = {
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and friendly matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["sarah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["james@mergington.edu", "lisa@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific concepts through experiments and projects",
            "schedule": "Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Create paintings, drawings, and other visual artwork",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["grace@mergington.edu", "ava@mergington.edu"]
        },
        "Music Band": {
            "description": "Play instruments and perform in school concerts",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["mason@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear current activities and restore original
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset again after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Test GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert "Debate Team" in data
    
    def test_get_activities_contains_correct_structure(self, reset_activities):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Basketball Team"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_get_activities_contains_participants(self, reset_activities):
        """Test that activities contain their participants"""
        response = client.get("/activities")
        data = response.json()
        
        basket_team = data["Basketball Team"]
        assert "alex@mergington.edu" in basket_team["participants"]
        
        debate_team = data["Debate Team"]
        assert "james@mergington.edu" in debate_team["participants"]
        assert "lisa@mergington.edu" in debate_team["participants"]


class TestSignupForActivity:
    """Test POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, reset_activities):
        """Test that signup adds participant to the activity"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Basketball%20Team/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball Team"]["participants"]
    
    def test_signup_nonexistent_activity_returns_404(self, reset_activities):
        """Test signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered_returns_400(self, reset_activities):
        """Test signing up a student already in the activity returns 400"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_full_activity_returns_400(self, reset_activities):
        """Test signing up for a full activity returns 400"""
        # Basketball Team has max 15 participants, currently has 1
        # Fill it up with test emails
        for i in range(14):
            email = f"student{i}@mergington.edu"
            client.post(f"/activities/Basketball%20Team/signup?email={email}")
        
        # Next signup should fail
        response = client.post(
            "/activities/Basketball%20Team/signup?email=overflow@mergington.edu"
        )
        assert response.status_code == 400
        assert "Activity is full" in response.json()["detail"]
    
    def test_signup_multiple_times_different_activities(self, reset_activities):
        """Test that a student can signup for multiple activities"""
        email = "student@mergington.edu"
        
        response1 = client.post(f"/activities/Basketball%20Team/signup?email={email}")
        assert response1.status_code == 200
        
        response2 = client.post(f"/activities/Tennis%20Club/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify both signups were successful
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball Team"]["participants"]
        assert email in data["Tennis Club"]["participants"]


class TestUnregisterFromActivity:
    """Test POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.post(
            "/activities/Basketball%20Team/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "alex@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self, reset_activities):
        """Test that unregister removes the participant"""
        client.post(
            "/activities/Basketball%20Team/unregister?email=alex@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "alex@mergington.edu" not in data["Basketball Team"]["participants"]
    
    def test_unregister_nonexistent_activity_returns_404(self, reset_activities):
        """Test unregister from nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered_returns_400(self, reset_activities):
        """Test unregistering a student not in the activity returns 400"""
        response = client.post(
            "/activities/Basketball%20Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_decreases_participant_count(self, reset_activities):
        """Test that unregister decreases the participant count"""
        # First get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Debate Team"]["participants"])
        
        # Unregister a participant
        client.post(
            "/activities/Debate%20Team/unregister?email=james@mergington.edu"
        )
        
        # Check new count
        response = client.get("/activities")
        new_count = len(response.json()["Debate Team"]["participants"])
        
        assert new_count == initial_count - 1


class TestSignupAndUnregisterFlow:
    """Test signup and unregister together"""
    
    def test_signup_then_unregister(self, reset_activities):
        """Test signup followed by unregister"""
        email = "student@mergington.edu"
        
        # Sign up
        response1 = client.post(f"/activities/Science%20Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert email in response.json()["Science Club"]["participants"]
        
        # Unregister
        response2 = client.post(f"/activities/Science%20Club/unregister?email={email}")
        assert response2.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert email not in response.json()["Science Club"]["participants"]
    
    def test_signup_unregister_frees_up_space(self, reset_activities):
        """Test that unregistering frees up space for new signups"""
        # Create a nearly full activity for testing
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Sign up email1
        client.post(f"/activities/Basketball%20Team/signup?email={email1}")
        
        # Basketball Team has 15 max, currently has 2 participants
        # Fill all remaining spots
        for i in range(13):
            client.post(f"/activities/Basketball%20Team/signup?email=filler{i}@mergington.edu")
        
        # Verify activity is full
        response = client.post(f"/activities/Basketball%20Team/signup?email={email2}")
        assert response.status_code == 400
        
        # Unregister email1
        client.post(f"/activities/Basketball%20Team/unregister?email={email1}")
        
        # Now email2 should be able to signup
        response = client.post(f"/activities/Basketball%20Team/signup?email={email2}")
        assert response.status_code == 200
