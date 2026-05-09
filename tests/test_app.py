"""
FastAPI backend tests using AAA (Arrange-Act-Assert) testing pattern.

Each test follows this structure:
- Arrange: Set up test data and preconditions
- Act: Perform the action being tested
- Assert: Verify expected outcomes and side effects
"""

import copy
import json

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def setup_function():
    reset_activities()


def test_root_redirects_to_static_index():
    # Arrange - No special setup needed

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    # Arrange - No special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Basketball Team"
    email = "alicia@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", json={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # This email is already signed up

    # Act
    response = client.post(f"/activities/{activity_name}/signup", json={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Already signed up for this activity"


def test_signup_unknown_activity_returns_404():
    # Arrange
    unknown_activity = "UnknownClub"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{unknown_activity}/signup", json={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # This email is already signed up

    # Act
    response = client.request(
        "DELETE",
        f"/activities/{activity_name}/participants",
        json={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "noone@mergington.edu"  # This email is not signed up

    # Act
    response = client.request(
        "DELETE",
        f"/activities/{activity_name}/participants",
        json={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
