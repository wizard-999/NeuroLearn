from __future__ import annotations


def get_next_level(score: float, reading_time: float) -> str:
    """
    Basic adaptive rule engine based on quiz score and reading time (minutes).
    """
    if reading_time and reading_time > 30:
        return "simpler"
    if score >= 80:
        return "harder"
    if 50 <= score < 80:
        return "same"
    return "simpler"

