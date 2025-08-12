#!/bin/bash
BASE_URL="http://127.0.0.1:5000"
EMAIL="alice@example.com"
NAME="Alice Test"

function run_curl() {
  local method=$1
  local url=$2
  local data=$3

  if [ -n "$data" ]; then
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X "$method" \
      -H "Content-Type: application/json" \
      -d "$data" "$url")
  else
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X "$method" "$url")
  fi

  body=$(echo "$response" | sed -e '/HTTP_STATUS:/d')
  status=$(echo "$response" | grep HTTP_STATUS | cut -d: -f2)
  echo "$body"
  return $status
}

echo "=== 1. Fetching available classes ==="
CLASSES_JSON=$(curl -s "$BASE_URL/classes?tz=Asia/Kolkata")
echo "$CLASSES_JSON" | jq .

CLASS_ID=$(echo "$CLASSES_JSON" | jq '.[] | select(.slots_available > 0) | .id' | head -n 1)

if [ -z "$CLASS_ID" ]; then
  echo "❌ No classes with available slots found."
  exit 1
fi

echo "Selected class_id: $CLASS_ID"
echo

echo "=== 2. Booking class $CLASS_ID ==="
BOOK_JSON=$(jq -n \
  --argjson class_id "$CLASS_ID" \
  --arg name "$NAME" \
  --arg email "$EMAIL" \
  '{class_id: $class_id, client_name: $name, client_email: $email}')

BOOK_RESPONSE=$(run_curl POST "$BASE_URL/book" "$BOOK_JSON")
echo "$BOOK_RESPONSE" | jq .

BOOK_MSG=$(echo "$BOOK_RESPONSE" | jq -r '.message // empty')

if [[ "$BOOK_MSG" != "Booking successful" ]]; then
  echo "❌ Booking failed."
  exit 1
fi

echo
echo "=== 3. Verifying booking via /bookings ==="
BOOKINGS_RESPONSE=$(run_curl GET "$BASE_URL/bookings?email=$EMAIL")
echo "$BOOKINGS_RESPONSE" | jq .

BOOK_FOUND=$(echo "$BOOKINGS_RESPONSE" | jq --argjson cid "$CLASS_ID" 'map(select(.class_id == $cid)) | length')

if [ "$BOOK_FOUND" -gt 0 ]; then
  echo "✅ Booking flow working"
  exit 0
else
  echo "❌ Booking not found in /bookings"
  exit 1
fi
