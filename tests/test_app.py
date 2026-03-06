"""
Tests for the Mergington High School Management System API.

This module contains comprehensive tests for all FastAPI endpoints using the
AAA (Arrange-Act-Assert) testing pattern, including success cases, error cases,
and edge cases.
"""

import pytest


class TestRootEndpoint:
    """Tests for the root endpoint (/)."""

    def test_root_redirect(self, client):
        """
        Test that the root endpoint redirects to the static index.html.

        AAA Pattern:
        - Arrange: Set up test client
        - Act: Make GET request to root endpoint
        - Assert: Verify redirect response
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code in [307, 308]  # Redirect status codes
        assert "/static/index.html" in response.headers["location"]


class TestActivitiesEndpoint:
    """Tests for the activities endpoint (/activities)."""

    def test_get_activities_success(self, client):
        """
        Test successfully retrieving all activities.

        AAA Pattern:
        - Arrange: Ensure activities are loaded
        - Act: Make GET request to activities endpoint
        - Assert: Verify response contains all expected activities
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # Should have 9 activities

        # Verify structure of each activity
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Tennis Club", "Art Studio", "Music Ensemble", "Robotics Club", "Debate Team"
        ]

        for activity_name in expected_activities:
            assert activity_name in data
            activity = data[activity_name]
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)
            assert activity["max_participants"] > 0

    def test_get_activities_structure(self, client):
        """
        Test that activities have the correct data structure.

        AAA Pattern:
        - Arrange: Activities are loaded via fixture
        - Act: Retrieve activities
        - Assert: Verify each activity has required fields with correct types
        """
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity["description"], str)
            assert isinstance(activity["schedule"], str)
            assert isinstance(activity["max_participants"], int)
            assert isinstance(activity["participants"], list)
            # All participants should be email strings
            for participant in activity["participants"]:
                assert isinstance(participant, str)
                assert "@mergington.edu" in participant


class TestSignupEndpoint:
    """Tests for the signup endpoint (/activities/{activity_name}/signup)."""

    def test_signup_success(self, client):
        """
        Test successfully signing up for an existing activity.

        AAA Pattern:
        - Arrange: Choose an activity and new email
        - Act: Make POST request to signup endpoint
        - Assert: Verify success response and participant was added
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"

        # Get initial participant count
        initial_response = client.get("/activities")
        initial_participants = len(initial_response.json()[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_email in data["message"]
        assert activity_name in data["message"]

        # Verify participant was actually added
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        assert len(final_participants) == initial_participants + 1
        assert new_email in final_participants

    def test_signup_nonexistent_activity(self, client):
        """
        Test signing up for a non-existent activity.

        AAA Pattern:
        - Arrange: Use invalid activity name
        - Act: Attempt to signup
        - Assert: Verify 404 error response
        """
        # Act
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "test@mergington.edu"}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_duplicate_participant(self, client):
        """
        Test signing up a participant who is already registered.

        AAA Pattern:
        - Arrange: Get an existing participant from an activity
        - Act: Try to signup the same person again
        - Assert: Verify 400 error for duplicate registration
        """
        # Arrange - Get an existing participant
        activities_response = client.get("/activities")
        chess_club = activities_response.json()["Chess Club"]
        existing_email = chess_club["participants"][0]

        # Act - Try to signup the same person again
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    @pytest.mark.parametrize("activity_name", [
        "Chess Club", "Programming Class", "Gym Class"
    ])
    def test_signup_multiple_activities(self, client, activity_name):
        """
        Test signing up for multiple different activities.

        AAA Pattern:
        - Arrange: Use parametrized activity names
        - Act: Signup for each activity
        - Assert: Verify successful registration for each
        """
        # Arrange
        test_email = f"multiactivity{activity_name.replace(' ', '')}@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert test_email in data["message"]
        assert activity_name in data["message"]


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint (/activities/{activity_name}/participants/{email})."""

    def test_unregister_success(self, client):
        """
        Test successfully unregistering from an activity.

        AAA Pattern:
        - Arrange: Get an existing participant
        - Act: Make DELETE request to unregister
        - Assert: Verify success and participant was removed
        """
        # Arrange
        activity_name = "Chess Club"
        activities_response = client.get("/activities")
        initial_participants = activities_response.json()[activity_name]["participants"]
        email_to_remove = initial_participants[0]
        initial_count = len(initial_participants)

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email_to_remove}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email_to_remove in data["message"]
        assert activity_name in data["message"]

        # Verify participant was actually removed
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        assert len(final_participants) == initial_count - 1
        assert email_to_remove not in final_participants

    def test_unregister_nonexistent_activity(self, client):
        """
        Test unregistering from a non-existent activity.

        AAA Pattern:
        - Arrange: Use invalid activity name
        - Act: Attempt to unregister
        - Assert: Verify 404 error response
        """
        # Act
        response = client.delete(
            "/activities/Nonexistent Club/participants/test@mergington.edu"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_nonexistent_participant(self, client):
        """
        Test unregistering a participant who is not signed up.

        AAA Pattern:
        - Arrange: Use valid activity but email not in participants
        - Act: Attempt to unregister
        - Assert: Verify 404 error response
        """
        # Act
        response = client.delete(
            "/activities/Chess Club/participants/notsignedup@mergington.edu"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()

    def test_unregister_and_reregister(self, client):
        """
        Test unregistering and then re-registering the same participant.

        AAA Pattern:
        - Arrange: Unregister a participant
        - Act: Re-register the same participant
        - Assert: Verify successful re-registration
        """
        # Arrange
        activity_name = "Programming Class"
        activities_response = client.get("/activities")
        initial_participants = activities_response.json()[activity_name]["participants"]
        email = initial_participants[0]

        # First unregister
        unregister_response = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert unregister_response.status_code == 200

        # Act - Re-register
        register_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert register_response.status_code == 200
        data = register_response.json()
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify they're back in the list
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        assert email in final_participants


class TestIntegrationScenarios:
    """Integration tests for complex user scenarios."""

    def test_full_participant_lifecycle(self, client):
        """
        Test complete lifecycle: signup → verify → unregister → verify.

        AAA Pattern:
        - Arrange: Start with clean state
        - Act: Perform signup, then unregister
        - Assert: Verify state changes throughout
        """
        # Arrange
        activity_name = "Gym Class"
        test_email = "lifecycle@mergington.edu"

        # Act & Assert - Initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        assert test_email not in initial_participants

        # Act & Assert - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        assert signup_response.status_code == 200

        # Verify signup
        mid_response = client.get("/activities")
        mid_participants = mid_response.json()[activity_name]["participants"]
        assert test_email in mid_participants

        # Act & Assert - Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/participants/{test_email}")
        assert unregister_response.status_code == 200

        # Verify unregistration
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        assert test_email not in final_participants

    def test_multiple_participants_same_activity(self, client):
        """
        Test multiple participants signing up for the same activity.

        AAA Pattern:
        - Arrange: Multiple test emails
        - Act: Signup multiple participants
        - Assert: Verify all are registered correctly
        """
        # Arrange
        activity_name = "Art Studio"
        test_emails = [
            "participant1@mergington.edu",
            "participant2@mergington.edu",
            "participant3@mergington.edu"
        ]

        # Act - Signup all participants
        for email in test_emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert - Verify all are registered
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]

        for email in test_emails:
            assert email in final_participants