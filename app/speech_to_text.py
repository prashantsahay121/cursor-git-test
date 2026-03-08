import speech_recognition as sr
from langdetect import detect

recognizer = sr.Recognizer()
mic = sr.Microphone()

WAKE_VARIANTS = [
    "casper","kasper","caspar"
]


def listen_once(mode="wake"):

    with mic as source:

        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:

        text = recognizer.recognize_google(audio)
        text = text.lower()

        if mode == "wake":
            print("Heard: Casper")
        else:
            print("Heard:", text)

        return text

    except:
        return None


def _detect_by_keywords(text):
    """Fallback: detect Hindi by common Hindi/Hinglish words."""
    text_lower = text.lower().strip()
    if not text_lower:
        return "english"
    hindi_words = [
        "kya", "kyu", "kyon", "nahi", "nahin", "kaise",
        "mera", "meri", "kar", "raha", "karun", "karne",
        "thik", "sahi", "band", "chal", "hai", "ho",
        "aapka", "apka", "thanda", "garam", "karo", "kiya",
        "karo", "hain", "kya", "kab", "kahan", "kaun",
    ]
    words = text_lower.split()
    for w in words:
        if w in hindi_words:
            return "hindi"
    return "english"


def detect_language(text):
    """
    Detect if the user is speaking Hindi or English.
    Uses langdetect when possible, with keyword fallback for short/ambiguous text.
    Returns "hindi" or "english".
    """
    if not text or not str(text).strip():
        return "english"

    text_clean = str(text).strip()
    try:
        if len(text_clean) >= 3:
            lang_code = detect(text_clean)
            if lang_code == "hi":
                return "hindi"
            if lang_code == "en":
                return "english"
    except Exception:
        pass
    return _detect_by_keywords(text_clean)