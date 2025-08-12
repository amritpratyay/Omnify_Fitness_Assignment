"""
utils.py

Utility functions for datetime parsing, timezone conversion, and email validation.
"""

from datetime import datetime
from dateutil import parser
import re
import logging

# zoneinfo compatibility: works on Python 3.9+ or uses backports on 3.8
try:
    from zoneinfo import ZoneInfo
except Exception:
    from backports.zoneinfo import ZoneInfo

# Configure logger for this module
logger = logging.getLogger(__name__)

IST_ZONE = ZoneInfo("Asia/Kolkata")
EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


def parse_ist_datetime(dt_str: str) -> datetime:
    """
    Parse an input datetime string and return an aware datetime in IST.
    Accepts naive or timezone-aware strings.

    Args:
        dt_str (str): Datetime string.

    Returns:
        datetime: Timezone-aware datetime in IST.
    """
    try:
        dt = parser.parse(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=IST_ZONE)
            logger.debug(f"Parsed naive datetime '{dt_str}' as IST: {dt}")
        else:
            dt = dt.astimezone(IST_ZONE)
            logger.debug(f"Converted aware datetime '{dt_str}' to IST: {dt}")
        return dt
    except Exception as e:
        logger.error(f"Failed to parse IST datetime from '{dt_str}': {e}")
        raise


def convert_ist_to_tz(dt_ist_str: str, tz_name: str) -> str:
    """
    Convert stored IST datetime string to target tz (IANA name).
    Returns ISO formatted string with offset.

    Args:
        dt_ist_str (str): IST datetime string.
        tz_name (str): IANA timezone name.

    Returns:
        str: ISO formatted datetime string in target timezone.
    """
    try:
        ist_dt = parse_ist_datetime(dt_ist_str)
        target = ZoneInfo(tz_name)
        converted = ist_dt.astimezone(target).isoformat()
        logger.debug(f"Converted IST '{dt_ist_str}' to {tz_name}: {converted}")
        return converted
    except Exception as e:
        logger.error(f"Timezone conversion failed from IST '{dt_ist_str}' to {tz_name}: {e}")
        raise


def ist_to_utc_iso(dt_ist_str: str) -> str:
    """
    Convert IST datetime string to UTC ISO format.

    Args:
        dt_ist_str (str): IST datetime string.

    Returns:
        str: ISO formatted UTC datetime string.
    """
    try:
        ist_dt = parse_ist_datetime(dt_ist_str)
        converted = ist_dt.astimezone(ZoneInfo("UTC")).isoformat()
        logger.debug(f"Converted IST '{dt_ist_str}' to UTC: {converted}")
        return converted
    except Exception as e:
        logger.error(f"Failed to convert IST '{dt_ist_str}' to UTC: {e}")
        raise


def validate_email(email: str) -> bool:
    """
    Validate an email address using a regex.

    Args:
        email (str): Email address.

    Returns:
        bool: True if valid, False otherwise.
    """
    is_valid = bool(EMAIL_RE.match(email))
    if is_valid:
        logger.debug(f"Validated email: {email}")
    else:
        logger.warning(f"Invalid email format: {email}")
    return is_valid


def convert_to_timezone(dt_str: str, target_tz: str) -> str:
    """
    Converts a datetime string in IST to the given timezone and returns ISO string.

    Args:
        dt_str (str): Datetime string in IST.
        target_tz (str): Target timezone (IANA name).

    Returns:
        str: ISO formatted datetime string in target timezone.
    """
    try:
        dt_ist = datetime.fromisoformat(dt_str)
        converted = dt_ist.replace(tzinfo=ZoneInfo("Asia/Kolkata")).astimezone(ZoneInfo(target_tz)).isoformat()
        logger.debug(f"Converted '{dt_str}' IST to {target_tz}: {converted}")
        return converted
    except Exception as e:
        logger.error(f"Failed to convert '{dt_str}' IST to {target_tz}: {e}")
        raise
