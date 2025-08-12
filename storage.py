"""
storage.py

Provides thread-safe functions for loading and saving fitness class and booking data
to a JSON file. Includes logging for all operations.
"""

import json
import os
import logging
from threading import Lock

# Configure logger for this module
logger = logging.getLogger(__name__)

DATA_FILE = "data.json"
_lock = Lock()


def _load_data():
    """
    Load data from the JSON file.

    Returns:
        dict: Dictionary with keys 'classes' and 'bookings'.
    """
    if not os.path.exists(DATA_FILE):
        logger.warning(f"Data file {DATA_FILE} not found. Initializing empty data store.")
        return {"classes": [], "bookings": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug(f"Loaded data from {DATA_FILE}: {len(data.get('classes', []))} classes, {len(data.get('bookings', []))} bookings")
        return data
    except Exception as e:
        logger.error(f"Failed to load {DATA_FILE}: {e}")
        return {"classes": [], "bookings": []}


def _save_data(data):
    """
    Save the given data dict to the JSON file (thread-safe).

    Args:
        data (dict): Data to save, must contain 'classes' and 'bookings' keys.

    Raises:
        Exception: If saving fails.
    """
    with _lock:
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved data to {DATA_FILE}")
        except Exception as e:
            logger.error(f"Failed to save {DATA_FILE}: {e}")
            raise


def load_classes():
    """
    Retrieve the list of classes from the data store.

    Returns:
        list: List of class dictionaries.
    """
    classes = _load_data()["classes"]
    logger.debug(f"Loaded {len(classes)} classes")
    return classes


def save_classes(classes):
    """
    Overwrite the list of classes in the data store.

    Args:
        classes (list): List of class dictionaries.
    """
    data = _load_data()
    data["classes"] = classes
    _save_data(data)
    logger.info(f"Updated classes list: {len(classes)} total")


def load_bookings():
    """
    Retrieve the list of bookings from the data store.

    Returns:
        list: List of booking dictionaries.
    """
    bookings = _load_data()["bookings"]
    logger.debug(f"Loaded {len(bookings)} bookings")
    return bookings


def add_booking(booking):
    """
    Add a booking entry to the data store.

    Args:
        booking (dict): Booking dictionary to add.
    """
    data = _load_data()
    booking["id"] = len(data["bookings"]) + 1
    data["bookings"].append(booking)
    _save_data(data)
    logger.info(f"Added booking ID {booking['id']} for class {booking['class_id']} by {booking['client_email']}")
