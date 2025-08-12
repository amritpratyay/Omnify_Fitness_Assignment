"""
app.py

Flask application providing API endpoints for fitness class listing, booking, and admin class creation.
"""

from flask import Flask, request, jsonify
from datetime import datetime
from zoneinfo import ZoneInfo
import re
import threading
import logging

import storage

from dateutil import parser



# Create a custom logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Capture everything, filter in handlers if needed

# Formatter for all logs
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# File handler - logs everything to app.log
file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Console handler - shows INFO and above in terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


app = Flask(__name__)
lock = threading.Lock()

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
IST = ZoneInfo("Asia/Kolkata")

@app.route("/classes", methods=["GET"])
def get_classes():
    """
    GET /classes?tz=<IANA timezone>
    List all available fitness classes.
    If 'tz' is provided, converts class datetimes to the given IANA timezone.
    If not, returns datetimes in UTC ISO format.
    Returns:
        JSON list of classes.
    """
    tz_param = request.args.get("tz", "Asia/Kolkata")
    logger.info(f"Fetching classes with timezone: {tz_param}")
    classes = storage.load_classes()

    result = []
    for c in classes:
        try:
            dt_ist = datetime.fromisoformat(c["datetime_ist"])
            dt_converted = dt_ist.replace(
                tzinfo=ZoneInfo("Asia/Kolkata")
            ).astimezone(ZoneInfo(tz_param))
            c_copy = c.copy()
            c_copy["datetime"] = dt_converted.isoformat()
            result.append(c_copy)
        except Exception as e:
            logger.error(f"Timezone conversion failed for class ID {c['id']}: {e}")
            result.append(c)
    logger.info(f"Returned {len(result)} classes")
    return jsonify(result)


@app.route("/book", methods=["POST"])
def book_class():
    """
    POST /book
    Book a slot in a fitness class.
    Request JSON: { "class_id": int, "client_name": str, "client_email": str }
    Returns:
        JSON with booking confirmation or error.
    """
    data = request.get_json(force=True, silent=True)
    if not data:
        logger.warning("Booking failed - Invalid or missing JSON payload")
        return jsonify({"error": "Invalid or missing JSON"}), 400

    class_id = data.get("class_id")
    client_name = data.get("client_name")
    client_email = data.get("client_email")

    # Basic validation
    if not all([class_id, client_name, client_email]):
        logger.warning(f"Booking failed - Missing fields: {data}")
        return jsonify({"error": "class_id, client_name, and client_email are required"}), 400

    if not re.match(EMAIL_REGEX, client_email):
        logger.warning(f"Booking failed - Invalid email: {client_email}")
        return jsonify({"error": "Invalid email format"}), 400

    classes = storage.load_classes()
    selected_class = next((c for c in classes if c["id"] == class_id), None)
    if not selected_class:
        logger.warning(f"Booking failed - Class not found: {class_id}")
        return jsonify({"error": "Class not found"}), 404

    if selected_class["slots_available"] <= 0:
        logger.info(f"Booking attempt - No slots for class {class_id} by {client_email}")
        return jsonify({"error": "No slots available"}), 400

    # Prevent race condition
    with lock:
        classes = storage.load_classes()  # reload in lock
        selected_class = next((c for c in classes if c["id"] == class_id), None)
        if selected_class["slots_available"] <= 0:
            logger.info(f"Booking attempt - No slots for class {class_id} by {client_email} (after lock check)")
            return jsonify({"error": "No slots available"}), 400

        selected_class["slots_available"] -= 1
        storage.save_classes(classes)

        booking = {
            "class_id": class_id,
            "client_name": client_name,
            "client_email": client_email,
            "booked_at": datetime.utcnow().isoformat() + "Z"
        }
        storage.add_booking(booking)

    logger.info(f"Booking success - Class {class_id} booked by {client_email}")
    return jsonify({"message": "Booking successful", "booking": booking}), 201


@app.route("/bookings", methods=["GET"])
def get_bookings():
    """
    GET /bookings?email=<email>
    List all bookings for a given client email.
    Returns:
        JSON list of bookings.
    """
    email = request.args.get("email")
    if not email:
        logger.warning("Bookings fetch failed - Missing email parameter")
        return jsonify({"error": "email parameter is required"}), 400

    bookings = storage.load_bookings()
    filtered = [b for b in bookings if b["client_email"] == email]
    logger.info(f"Fetched {len(filtered)} bookings for email: {email}")
    return jsonify(filtered)

@app.route("/admin/classes", methods=["POST"])
def add_class():
    """
    POST /admin/classes
    Admin endpoint to add a new class.
    Request JSON: { "name": str, "datetime_ist": "YYYY-MM-DDTHH:MM:SS", "instructor": str, "capacity": int }
    Returns:
        JSON with created class or error.
    """
    data = request.get_json(force=True, silent=True)
    if not data:
        logger.warning("Class creation failed - Invalid or missing JSON payload")
        return jsonify({"error": "Invalid or missing JSON"}), 400

    class_name = data.get("name")
    class_datetime_ist = data.get("datetime_ist")
    class_instructor = data.get("instructor")
    class_capacity = data.get("capacity")

    # Basic validation
    if not all([class_name, class_datetime_ist, class_instructor, class_capacity]):
        logger.warning(f"Class creation failed - Missing fields: {data}")
        return jsonify({"error": "name, datetime_ist, instructor, and capacity are required"}), 400

    try:
        parsed_datetime = parser.isoparse(class_datetime_ist)
        # If no timezone, default to IST
        if parsed_datetime.tzinfo is None:
            parsed_datetime = parsed_datetime.replace(tzinfo=IST)
    except Exception as e:
        logger.warning(f"Class creation failed - Invalid datetime_ist format: {e}")
        return jsonify({"error": "Invalid datetime_ist format"}), 400

    if not isinstance(class_capacity, int) or class_capacity <= 0:
        logger.warning(f"Class creation failed - Invalid capacity: {class_capacity}")
        return jsonify({"error": "Capacity must be a positive integer"}), 400

    # Create new class entry
    new_class = {
        "id": str(len(storage.load_classes()) + 1),
        "name": class_name,
        "datetime_ist": parsed_datetime.isoformat(),
        "instructor": class_instructor,
        "capacity": class_capacity,
        "slots_available": class_capacity
    }

    classes = storage.load_classes()
    classes.append(new_class)
    storage.save_classes(classes)

    logger.info(f"Class created successfully - ID: {new_class['id']}, Name: {class_name}")
    return jsonify({"message": "Class created successfully", "class": new_class}), 201



if __name__ == "__main__":
    app.run(debug=True, port=5000)
