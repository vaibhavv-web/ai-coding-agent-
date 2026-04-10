import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_response(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You return ONLY raw JSON. No markdown. No backticks. No explanation. All newlines in code must be escaped as \\n. All tabs must be escaped as \\t. Never include real newline characters inside JSON string values."
                 "CRITICAL: Inside JSON string values, you MUST: "
                        "1)escape all double quotes as \\\" "
                        "2) escape all newlines as \\n "
                        "3) escape all tabs as \\t "
                        "4) NEVER use triple quotes. "
                        "Failure to follow these rules makes the JSON invalid."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content

        if not content or content.strip() == "":
            return ""

        return content.strip()

    except Exception as e:
        print(" LLM ERROR:", e)
        return ""