from llm import generate_response
import json


def reviewer_agent(task, code , context):
    prompt = f"""
You are a strict code reviewer.

Your job is to review , evaluate and modify the code using codebase context 

Context:
{context}

Task:
{task}

Code:
{code}

Instructions:
- Analyze code quality
- Fix bugs and improve code if needed
- Give a quality score (0 to 10)
- Ensure code aligns with context
- Do NOT include backticks or explanations

Return in JSON format ONLY:

{{
  "score": number,
  "code": "improved code"
}}
"""

    response = generate_response(prompt)

    try:
        result = json.loads(response.text)
        return result
    except:
        return {
            "score": 5,
            "code": code
        }