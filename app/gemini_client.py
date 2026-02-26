import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv(".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash-lite")


def ask_gemini_with_image(image_path: str, question: str) -> str:
    image = Image.open(image_path)
    response = model.generate_content([question, image])
    return response.text