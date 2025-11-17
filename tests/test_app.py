import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    # Save original state
    original_activities = {
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
        },
        "Soccer Club": {
            "description": "Outdoor soccer practice and intramural matches",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 25,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team with regular practices and games",
            "schedule": "Mondays and Wednesdays, 5:00 PM - 7:00 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "william@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and mixed media projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["isabella@mergington.edu", "mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, stagecraft, and production of school plays",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["charlotte@mergington.edu", "amelia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Prepare for and compete in debate tournaments",
            "schedule": "Tuesdays, 5:00 PM - 7:00 PM",
            "max_participants": 20,
            "participants": ["ethan@mergington.edu", "oliver@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments, science fairs, and research projects",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "grace@mergington.edu"]
        }
    }
    
    yield
    
    # Restore original state
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, reset_activities):
        """Test that /activities endpoint returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities_data = response.json()
        assert len(activities_data) == 9
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        assert activities_data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


class TestSignUp:
    def test_signup_for_activity_success(self, reset_activities):
        """Test successful signup for an activity"""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in data["message"]
        
        # Verify the signup was recorded
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club"]["participants"]

    def test_signup_duplicate_email_fails(self, reset_activities):
        """Test that signing up with duplicate email fails"""
        email = "michael@mergington.edu"  # Already registered in Chess Club
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity_fails(self, reset_activities):
        """Test that signing up for nonexistent activity fails"""
        email = "newstudent@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestUnregister:
    def test_unregister_success(self, reset_activities):
        """Test successful unregister from an activity"""
        email = "michael@mergington.edu"  # Already registered in Chess Club
        activity = "Chess Club"
        
        # Verify participant is initially in the activity
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Chess Club"]["participants"]

    def test_unregister_not_registered_fails(self, reset_activities):
        """Test that unregistering a non-registered participant fails"""
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "not registered" in data["detail"].lower()

    def test_unregister_nonexistent_activity_fails(self, reset_activities):
        """Test that unregistering from nonexistent activity fails"""
        email = "michael@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()
