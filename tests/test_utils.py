from utils import convert_to_timezone
from zoneinfo import ZoneInfo

def test_convert_to_timezone():
    ist_time = "2025-08-15T07:30:00"
    converted = convert_to_timezone(ist_time, "America/New_York")
    # Ensure correct timezone
    assert converted.endswith("-04:00") or converted.endswith("-05:00")
    # Ensure conversion preserved time structure
    assert "T" in converted
