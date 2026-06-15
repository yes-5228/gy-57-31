from datetime import datetime


def duration_to_minutes(start: datetime, end: datetime) -> int:
    delta = end - start
    return int(delta.total_seconds() // 60)


def minutes_to_hours(minutes: int) -> float:
    return round(minutes / 60, 2)
