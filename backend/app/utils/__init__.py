from datetime import datetime


def calculate_duration_hours(start: datetime, end: datetime) -> float:
    return round((end - start).total_seconds() / 3600, 1)
