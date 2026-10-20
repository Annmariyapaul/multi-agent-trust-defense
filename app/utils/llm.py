import os
import time
import random

import httpx
from google import genai
from google.genai import errors
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_AI_API_KEY"))

MAX_RETRIES = 4

# gemini-2.0-flash was shut down in June 2026, so the old fallback could
# never succeed. Overridable from .env so a future retirement is a config
# change, not a code change.
FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL")

# 429 = rate limit / quota. Temporary, so worth waiting for, unlike other 4xx.
RETRYABLE_CLIENT_CODES = {429}


def _backoff(attempt):
    return (2 ** attempt) + random.uniform(0, 1)


def generate(prompt, agent_name="agent"):
    """Call Gemini with backoff. Returns (text, ok).

    ok=False means the agent could not produce output — the caller
    should treat that as a failed stage, not crash the workflow.
    """
    model = os.getenv("GEMINI_MODEL", FALLBACK_MODEL)

    for attempt in range(MAX_RETRIES):
        try:
            # Chat.send_message avoids the automatic-function-calling warning
            # emitted by newer google-genai versions for generate_content.
            chat = client.chats.create(model=model)
            response = chat.send_message(prompt)
            text = response.text
            if not text:
                # Safety-blocked, or no text parts in the response.
                print(f"[LLM] {agent_name}: empty response "
                      f"(model={model}) — treating as unavailable")
                return "[LLM_EMPTY]", False
            return text, True

        except errors.ServerError as e:
            reason = f"server busy ({e.code})"

        except errors.ClientError as e:
            if e.code not in RETRYABLE_CLIENT_CODES:
                print(f"[LLM] {agent_name}: client error {e.code} "
                      f"— not retrying")
                return f"[LLM_ERROR] {e.code}", False
            reason = f"rate limited ({e.code})"

            # A 429 is commonly project quota exhaustion. Retrying the same
            # model cannot repair that; try the configured fallback once.
            if FALLBACK_MODEL and model != FALLBACK_MODEL:
                print(f"[LLM] {agent_name}: falling back to {FALLBACK_MODEL}")
                model = FALLBACK_MODEL
                continue

        except httpx.TransportError as e:
            # Connection drops, timeouts. Not API errors, so they
            # previously escaped and would crash the graph.
            reason = f"network error ({type(e).__name__})"

        # Don't sleep after the final attempt — nothing left to retry.
        if attempt == MAX_RETRIES - 1:
            break

        wait = _backoff(attempt)
        print(f"[LLM] {agent_name}: {reason}, "
              f"retry {attempt + 1}/{MAX_RETRIES - 1} in {wait:.1f}s")
        time.sleep(wait)

    print(f"[LLM] {agent_name}: unavailable after {MAX_RETRIES} attempts")
    return "[LLM_UNAVAILABLE]", False