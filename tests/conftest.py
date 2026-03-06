"""
Pytest configuration and shared fixtures for the test suite.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test to ensure test isolation."""
    # Import here to avoid circular imports
    from src.app import activities

    # Store the initial state
    initial_activities = {
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
        "Basketball Team": {
            "description": "Competitive basketball training and matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis skills development and friendly competitions",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lucy@mergington.edu", "james@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Learn instruments and perform in concerts",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["grace@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots for competitions",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["ryan@mergington.edu", "isabella@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["david@mergington.edu"]
        }
    }

    # Reset the global activities dictionary
    activities.clear()
    activities.update(initial_activities)