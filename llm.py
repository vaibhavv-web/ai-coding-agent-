import json
import os
import time

from dotenv import dotenv_values, load_dotenv

load_dotenv(override=True)

_LAST_LLM_ERROR = ""


def _set_last_llm_error(message):
    global _LAST_LLM_ERROR
    _LAST_LLM_ERROR = message


def get_last_llm_error():
    return _LAST_LLM_ERROR


def _looks_like_google_api_key(value):
    return isinstance(value, str) and value.startswith("AIza")


def _get_gemini_api_key():
    env_file_values = dotenv_values(".env")
    candidates = [
        env_file_values.get("GEMINI_API_KEY"),
        env_file_values.get("GOOGLE_API_KEY"),
        env_file_values.get("GROQ_API_KEY"),
        os.getenv("GEMINI_API_KEY"),
        os.getenv("GOOGLE_API_KEY"),
        os.getenv("GROQ_API_KEY"),
    ]

    for candidate in candidates:
        value = (candidate or "").strip()
        if value:
            return value

    return ""


def generate_response(prompt, model=None, json_schema=None):
    _set_last_llm_error("")
    try:
        from google import genai
    except ImportError:
        message = "google-genai is not installed. Install it with: pip install google-genai"
        _set_last_llm_error(message)
        print("LLM ERROR:", message)
        return ""

    api_key = _get_gemini_api_key()
    if not api_key:
        message = "Gemini API key is missing. Set GEMINI_API_KEY, GOOGLE_API_KEY, or GROQ_API_KEY in .env."
        _set_last_llm_error(message)
        print("LLM ERROR:", message)
        return ""

    primary_model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    fallback_models = [
        primary_model,
        os.getenv("GEMINI_FALLBACK_MODEL_1", "gemini-2.5-flash"),
        os.getenv("GEMINI_FALLBACK_MODEL_2", "gemini-1.5-flash"),
    ]
    models_to_try = []
    for candidate in fallback_models:
        candidate = (candidate or "").strip()
        if candidate and candidate not in models_to_try:
            models_to_try.append(candidate)

    client = genai.Client(api_key=api_key)
    config = None
    if json_schema:
        config = {
            "response_mime_type": "application/json",
            "response_json_schema": json_schema,
        }

    last_error = ""
    for model_name in models_to_try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )

                if getattr(response, "parsed", None) is not None:
                    return json.dumps(response.parsed)

                text = (response.text or "").strip()
                if text.startswith("```"):
                    text = text.replace("```json", "").replace("```", "").strip()
                return text
            except Exception as e:
                last_error = str(e)
                retryable = "503" in last_error or "UNAVAILABLE" in last_error or "RESOURCE_EXHAUSTED" in last_error
                if retryable and attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                if retryable:
                    break
                _set_last_llm_error(last_error)
                print("LLM ERROR:", e)
                return ""

    _set_last_llm_error(last_error)
    if last_error:
        print("LLM ERROR:", last_error)
    return ""