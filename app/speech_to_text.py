import speech_recognition as sr

recognizer = sr.Recognizer()


def listen_for_wake_word():
    with sr.Microphone() as source:
        print("\n[Wake Mode] Say 'Casper' to activate...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
        except:
            print("No speech detected.")
            return False

        try:
            text = recognizer.recognize_google(audio).lower()
            print("Heard (wake check):", text)

            if "casper" in text or "kasper" in text:
                print("Wake word detected!")
                return True
            else:
                return False

        except Exception as e:
            print("Speech recognition error:", e)
            return False


def listen_for_question():
    with sr.Microphone() as source:
        print("\n[Question Mode] Ask your question now...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=6)
        except:
            print("No question detected.")
            return None

        try:
            text = recognizer.recognize_google(audio)
            print("Question captured:", text)
            return text
        except Exception as e:
            print("Question recognition error:", e)
            return None