import re
from unidecode import unidecode

DISPLAY_MARKER = "DISPLAY:"


def text_for_tts(text):
    """
    Prepare text for TTS so the engine reads full sentences.
    - Removes list numbers so TTS doesn't say only "1, 2, 3".
    - Replaces "..." so TTS doesn't say "dot dot dot".
    """
    if not text or not str(text).strip():
        return str(text) if text else ""
    t = str(text).strip()
    # Replace ellipses so TTS doesn't say "dot dot dot" (SAPI/Windows reads ... as "dot dot dot")
    t = re.sub(r"\.\s*\.\s*\.", " ", t)
    t = t.replace("\u2026", " ")  # Unicode ellipsis …
    # Remove number + ) or . at start of each line (e.g. "1) Observation" -> "Observation")
    t = re.sub(r"^\s*\d+[\.\)]\s*", "", t, flags=re.MULTILINE)
    # Replace inline step numbers "1. " "2. " with "Step one. " so TTS reads the sentence
    t = re.sub(r"\b1\.\s+", "Step one. ", t)
    t = re.sub(r"\b2\.\s+", "Step two. ", t)
    t = re.sub(r"\b3\.\s+", "Step three. ", t)
    t = re.sub(r"\b4\.\s+", "Step four. ", t)
    t = re.sub(r"\b5\.\s+", "Step five. ", t)
    # Remove any other inline "number. " (e.g. "६. " in Hindi) so TTS doesn't say the digit
    t = re.sub(r"\d+\.\s+", "", t)
    # Collapse multiple newlines and spaces, then trim
    t = re.sub(r"\n{2,}", "\n", t).strip()
    t = re.sub(r" {2,}", " ", t)
    t = t.strip(" \t.\u2026")
    # If we stripped too much and left nothing useful, return original
    if not t or len(t) < 3:
        return str(text).strip() if text else ""
    return t


def to_hinglish(text):
    """Convert Devanagari Hindi to Roman (Hinglish) using unidecode. Fallback only."""
    try:
        return unidecode(text)
    except Exception:
        return text


def split_hindi_response(response):
    """
    If Gemini returned Hindi + DISPLAY: Hinglish, return (hindi_for_tts, hinglish_for_terminal).
    Otherwise return (response, to_hinglish(response)).
    """
    if not response:
        return "", ""
    text = response.strip()
    if DISPLAY_MARKER in text:
        parts = text.split(DISPLAY_MARKER, 1)
        hindi_part = parts[0].strip()
        hinglish_part = parts[1].strip() if len(parts) > 1 else ""
        if not hinglish_part:
            hinglish_part = to_hinglish(hindi_part)
        return hindi_part, hinglish_part
    return text, to_hinglish(text)