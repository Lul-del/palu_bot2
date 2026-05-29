from datetime import time


def parse_time_hhmm(value: str) -> time | None:
    try:
        hh, mm = value.strip().split(":", 1)
        h = int(hh)
        m = int(mm)
        if h < 0 or h > 23 or m < 0 or m > 59:
            return None
        return time(hour=h, minute=m)
    except ValueError:
        return None
