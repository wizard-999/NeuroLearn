from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List


def award_points(score: float, reading_time: float) -> Dict[str, int]:
    """
    Awards points based on quiz score and efficient reading time.
    """
    points = max(int(score), 0)
    if reading_time > 0 and reading_time < 20:
        points += 10
    elif reading_time >= 20:
        points += 5
    return {"points": points}


def calculate_streak(dates_list: List[str]) -> Dict[str, int]:
    """
    dates_list should contain ISO date strings (YYYY-MM-DD).
    Calculates the longest consecutive streak ending today.
    """
    if not dates_list:
        return {"streak": 0}
    dates = sorted({datetime.fromisoformat(d).date() for d in dates_list})
    streak = 1
    longest = 1
    for prev, curr in zip(dates, dates[1:]):
        if curr - prev == timedelta(days=1):
            streak += 1
        else:
            longest = max(longest, streak)
            streak = 1
    longest = max(longest, streak)
    return {"streak": longest}


def get_badges(total_points: int, streak_days: int) -> Dict[str, str]:
    badges = []
    if total_points >= 500:
        badges.append("Master Reader")
    elif total_points >= 200:
        badges.append("Focused Scholar")
    elif total_points >= 100:
        badges.append("Learning Champ")

    if streak_days >= 14:
        badges.append("14-day streak")
    elif streak_days >= 7:
        badges.append("7-day streak")

    return {"badge": ", ".join(badges) if badges else ""}

