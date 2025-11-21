from __future__ import annotations

import pyttsx3


def _estimate_sentence_durations(text: str, rate: int) -> list[float]:
    # Rate is words per minute; convert to seconds per word.
    if rate <= 0:
        rate = 150
    seconds_per_word = 60.0 / rate

    durations = []
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    for sentence in sentences:
        word_count = max(len(sentence.split()), 1)
        durations.append(word_count * seconds_per_word)
    return durations


def speak_text(text: str, rate: int = 150) -> list[float]:
    """
    Speaks text locally via pyttsx3. Returns approximate durations per sentence
    for highlighting synchronization.
    """
    if not text:
        return []

    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.say(text)
    engine.runAndWait()

    return _estimate_sentence_durations(text, rate)

