import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv(".env")

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash-lite")


def ask_gemini_with_image(image_path, question, language, history):

    image = Image.open(image_path)

    # downscale image to reduce upload size and latency while preserving content
    try:
        image.thumbnail((1024, 1024))
    except Exception:
        # if resizing fails, continue with original image to preserve behavior
        pass

    # last few conversation messages
    history_text = "\n".join(history[-10:]) if history else "No previous conversation."

    if language == "english":
        language_instruction = """
Respond only in English.
"""
    else:
        language_instruction = """
Respond in Hindi (Devanagari script) only. Use simple sentences.
In the Hindi part use only Hindi—no English words.
Use Hindi section titles: प्रेक्षण, निदान, कार्यवाही, अनुवर्तन.

After the Hindi response add a new line:
DISPLAY:
Then write the same response in Hinglish (Roman script) for terminal display.
Do not use Devanagari in the DISPLAY part.
"""

    prompt = f"""

{language_instruction}

Previous conversation context:
{history_text}

You are an experienced HVAC field technician guiding another technician remotely to diagnose and fix an AC problem.

Use TWO inputs:
1) The user's question
2) The camera image

Your goal is to perform STEP-BY-STEP troubleshooting like a real technician.

Always respond in this EXACT structure.

Observation
Describe what you see in the image or what the user reported.

Diagnosis
Explain the most likely cause of the problem based on the question and image.

Action
Give ONLY the next troubleshooting step the technician should perform.
Explain clearly how to do that step.

Follow-up
Tell the user what to do next.

Troubleshooting rules:

Follow this troubleshooting order:

1. Indoor basic checks
   - AC mode and temperature setting
   - Air filter condition
   - Airflow blockage

2. Indoor mechanical checks
   - Evaporator coil condition
   - Indoor fan operation

3. Outdoor unit checks
   - Check if the outdoor unit is running
   - Check if the outdoor fan is spinning
   - Check if the compressor sound is present
   - Check if condenser coil is dirty

4. Cooling system checks
   - Possible refrigerant issue
   - Ice formation on coil
   - Air circulation problems

Rules:
- Start with the simplest checks.
- Give only ONE step at a time.
- NEVER repeat a troubleshooting step that is already done in the conversation.
- After indoor checks are completed, move to outdoor unit diagnostics.
- If indoor components are working correctly but cooling is still weak, prioritize checking the outdoor unit.
- Some steps are preparation steps (like opening the panel, removing the filter).
- If the step is preparation, do NOT ask the user to run the AC yet.
- Only ask to run the AC after a fixing step (like cleaning a filter).
- If the user says the problem is solved (e.g., "ho gaya", "problem solved"), give a short success message and stop troubleshooting.
- Do NOT suggest calling an electrician or technician.
- Be practical like a real HVAC technician.
- Keep answers concise and clear.

Current user issue:
{question}

"""

    response = model.generate_content([prompt, image])

    return response.text