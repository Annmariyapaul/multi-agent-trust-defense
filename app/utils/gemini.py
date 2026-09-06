'''
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


def ask_gemini(prompt):

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text
'''
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


def ask_gemini(prompt, retries=4):

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            return response.text

        except errors.ServerError as e:
            wait = 2 ** attempt
            print(f"[GEMINI] Server error ({e.code}), retrying in {wait}s "
                  f"(attempt {attempt + 1}/{retries})")
            time.sleep(wait)

        except errors.ClientError as e:
            print(f"[GEMINI] Client error: {e}")
            return None

    print("[GEMINI] All retries failed.")
    return None