import pytest
from app import app
import storage
from datetime import datetime

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_classes_default_timezone(client):
    rv = client.get("/classes")
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, list)
    assert "name" in data[0]


def test_booking_success(client):
    # Pick a class with available slots
    classes = storage.load_classes()
    class_id = next((c["id"] for c in classes if c["slots_available"] > 0), None)
    assert class_id is not None

    payload = {
        "class_id": class_id,
        "client_name": "Test User",
        "client_email": "test@example.com"
    }
    rv = client.post("/book", json=payload)
    assert rv.status_code == 201
    data = rv.get_json()
    assert data["message"] == "Booking successful"


def test_get_bookings(client):
    email = "test@example.com"
    rv = client.get(f"/bookings?email={email}")
    assert rv.status_code == 200
    data = rv.get_json()
    assert all(b["client_email"] == email for b in data)


# ==== Negative cases ====

def test_booking_invalid_class_id(client):
    payload = {
        "class_id": 9999,
        "client_name": "Test User",
        "client_email": "test@example.com"
    }
    rv = client.post("/book", json=payload)
    assert rv.status_code == 404
    assert "Class not found" in rv.get_json()["error"]


def test_booking_invalid_email_format(client):
    classes = storage.load_classes()
    class_id = next((c["id"] for c in classes if c["slots_available"] > 0), None)
    payload = {
        "class_id": class_id,
        "client_name": "Test User",
        "client_email": "invalid-email"
    }
    rv = client.post("/book", json=payload)
    assert rv.status_code == 400
    assert "Invalid email format" in rv.get_json()["error"]


def test_booking_no_slots(client):
    # Create a class with 0 slots
    classes = storage.load_classes()
    class_with_no_slots = next((c for c in classes if c["slots_available"] == 0), None)

    if not class_with_no_slots:
        # artificially create one
        classes[0]["slots_available"] = 0
        storage.save_classes(classes)
        class_with_no_slots = classes[0]

    payload = {
        "class_id": class_with_no_slots["id"],
        "client_name": "Test User",
        "client_email": "test@example.com"
    }
    rv = client.post("/book", json=payload)
    assert rv.status_code == 400
    assert "No slots available" in rv.get_json()["error"]


def test_booking_missing_fields(client):
    rv = client.post("/book", json={"class_id": 1})
    assert rv.status_code == 400
    assert "required" in rv.get_json()["error"]
