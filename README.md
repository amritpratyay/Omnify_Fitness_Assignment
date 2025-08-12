# 🏋️‍♀️ Fitness Studio Booking API

A simple **Python + Flask** backend for a fictional fitness studio.  
Supports viewing classes, booking spots, and fetching bookings by client email.  
Includes timezone conversion (IST → requested timezone).

---

## 📦 Features

- **GET `/classes`** → List all upcoming classes (with IST and converted time).
- **POST `/book`** → Book a class by ID, validate availability & reduce slots.
- **GET `/bookings`** → Get all bookings for a specific email.
- **POST `/admin/classes`** → Admin endpoint to add new classes.
- Timezone-aware scheduling (default IST).
- Input validation & logging.
- In-memory (JSON file) storage.

---

## 🛠 Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/fitness-booking.git
cd fitness-booking
```

### 2️⃣ Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Run the server
```bash
python3 app.py
```

---

## 📋 API Endpoints & Sample Requests

### 1. Get all classes
```bash
curl -X GET "http://127.0.0.1:5000/classes?tz=Asia/Tokyo"
```
- `tz` parameter is optional (default = `Asia/Kolkata`).

---

### 2. Book a class
```bash
curl -X POST "http://127.0.0.1:5000/book" \
-H "Content-Type: application/json" \
-d '{
  "class_id": 1,
  "client_name": "John Doe",
  "client_email": "john@example.com"
}'
```

---

### 3. Get bookings by email
```bash
curl -X GET "http://127.0.0.1:5000/bookings?email=john@example.com"
```

---

### 4. Add a new class (Admin only)
```bash
curl -X POST "http://127.0.0.1:5000/admin/classes" \
-H "Content-Type: application/json" \
-d '{
  "name": "Evening Zumba",
  "datetime_ist": "2025-08-15T18:00:00",
  "instructor": "Riya Mehta",
  "capacity": 20
}'
```
> **Note:** `datetime_ist` can be with or without timezone offset (e.g., `+05:30`).  
> If no timezone is given, IST will be applied automatically.

---

## 🧪 Running Tests
```bash
pytest -v
```

---

## 📂 Project Structure
```plaintext
.
├── app.py            # Main Flask app
├── storage.py        # Data persistence
├── utils.py          # Timezone & validation helpers
├── data.json         # Seed data storage
├── requirements.txt  # Python dependencies
├── README.md         # Documentation
└── tests/
    └── test_api.py   # Unit tests
```

---

## 📌 Notes
- All times are stored in IST internally.
- Logs are stored in `app.log`.
- No full database setup required — all data is stored in `data.json`.
