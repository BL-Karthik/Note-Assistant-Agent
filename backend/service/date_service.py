
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def extract_meeting_date(message: str, date_direction: str = "NONE"):

    # Get today's date using Indian timezone
    reference_date = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).date()

    text = message.lower()
    date_direction = date_direction.upper()

    print("\n---------- DATE EXTRACTION ----------")
    print("REFERENCE DATE:", reference_date)
    print("INPUT MESSAGE:", message)
    print("DATE DIRECTION:", date_direction)

    # Day before yesterday
    if "day before yesterday" in text:
        result = reference_date - timedelta(days=2)
        print("EXTRACTED DATE:", result)
        return result

    # Day after tomorrow
    if "day after tomorrow" in text:
        result = reference_date + timedelta(days=2)
        print("EXTRACTED DATE:", result)
        return result

    # Yesterday
    if "yesterday" in text:
        result = reference_date - timedelta(days=1)
        print("EXTRACTED DATE:", result)
        return result

    # Tomorrow
    if "tomorrow" in text:
        result = reference_date + timedelta(days=1)
        print("EXTRACTED DATE:", result)
        return result

    # Today
    if "today" in text:
        print("EXTRACTED DATE:", reference_date)
        return reference_date

    # After / in N days
    match = re.search(
        r"\b(?:after|in)\s+(\d+)\s+days?\b",
        text
    )

    if match:
        result = reference_date + timedelta(days=int(match.group(1)))
        print("EXTRACTED DATE:", result)
        return result

    # N days later / from now
    match = re.search(
        r"\b(\d+)\s+days?\s+(?:later|from now)\b",
        text
    )

    if match:
        result = reference_date + timedelta(days=int(match.group(1)))
        print("EXTRACTED DATE:", result)
        return result

    # N days ago
    match = re.search(
        r"\b(\d+)\s+days?\s+ago\b",
        text
    )

    if match:
        result = reference_date - timedelta(days=int(match.group(1)))
        print("EXTRACTED DATE:", result)
        return result

    # Weekday handling
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }

    weekday_pattern = (
        r"\b(last|next)?\s*("
        + "|".join(weekdays.keys())
        + r")\b"
    )

    match = re.search(weekday_pattern, text)

    if match:

        modifier = match.group(1)
        target_weekday = weekdays[match.group(2)]

        today_weekday = reference_date.weekday()

        days_difference = (
            target_weekday - today_weekday
        ) % 7

        if modifier == "last":
            days_difference = -(
                (today_weekday - target_weekday) % 7 or 7
            )

        elif modifier == "next":
            days_difference = days_difference or 7

        elif date_direction == "PAST":
            days_difference = -(
                (today_weekday - target_weekday) % 7 or 7
            )

        elif date_direction in ("FUTURE", "NONE"):
            days_difference = days_difference

        elif date_direction == "TODAY":
            print("EXTRACTED DATE:", reference_date)
            return reference_date

        result = reference_date + timedelta(days=days_difference)
        print("EXTRACTED DATE:", result)
        return result

    # No date mentioned: do not apply a date filter
    print("No date mentioned. Skipping date filter.")
    return None


def extract_meeting_dates(message: str):

    text = message.lower()

    conversation_date = None
    meeting_date = None

    # Extract past conversation date
    past_keywords = [
        "day before yesterday",
        "yesterday"
    ]

    for keyword in past_keywords:
        if keyword in text:
            conversation_date = extract_meeting_date(
                keyword,
                date_direction="PAST"
            )
            break

    # Extract future meeting date
    future_keywords = [
        "day after tomorrow",
        "tomorrow"
    ]

    for keyword in future_keywords:
        if keyword in text:
            meeting_date = extract_meeting_date(
                keyword,
                date_direction="FUTURE"
            )
            break

    return {
        "conversation_date": conversation_date,
        "meeting_date": meeting_date
    }

