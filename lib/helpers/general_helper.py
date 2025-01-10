from datetime import datetime


def shorten_description(description, word_limit=3):
    words = description.split()
    if len(words) > word_limit:
        return " ".join(words[:word_limit]) + "..."
    else:
        return description


def validate_dates(start_date, end_date):
    # Check if either date is None or empty
    if not start_date or not end_date:
        print("Start date or end date is missing or invalid.")
        return False

    try:
        # Convert the string dates to datetime objects
        s_date = datetime.fromisoformat(start_date)
        e_date = datetime.fromisoformat(end_date)
    except ValueError as e:
        print(f"Error parsing dates: {e}")
        return False

    # Check if end_date is before start_date
    if e_date < s_date:
        print("End date cannot be before start date.")
        return False

    return True
