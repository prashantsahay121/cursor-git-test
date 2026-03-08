import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv(".env")

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash-lite")


def ask_gemini_with_image(image_path, question, language):

    image = Image.open(image_path)

    if language == "english":
        language_instruction = """
Respond only in English.
"""
    else:
        language_instruction = """
Respond in Hindi (Devanagari script) only. Use simple sentences.
In the Hindi part use only Hindi—no English words. Use Hindi section titles: प्रेक्षण (for observation), निदान (for diagnosis), कार्यवाही (for action), अनुवर्तन (for follow-up). Do not write Observation, Diagnosis, Action, Follow-up in the Hindi response.
After your Hindi response, add exactly one new line, then the line: DISPLAY:
Then on the next line write the same response in Hinglish (Roman script) for terminal display. Do not use Devanagari in the DISPLAY part.
"""

    prompt = f"""

{language_instruction}

You are an HVAC technician helping fix AC problems. You must always give your answer in this exact structure:

1) Observation — What you see in the image or from the user's issue (what is wrong or visible).
2) Diagnosis — What is likely causing the problem.
3) Action — Clear steps the user should take to fix it (number the steps).
4) Follow-up — What to check after or when to call a technician.

Do not skip any of these four parts. Be specific and practical. Use full sentences only; do not use ellipsis (...).

User issue:
{question}
"""

    response = model.generate_content([prompt,image])

    return response.text