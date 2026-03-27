from llm import generate_response



def coder_agent(task, plan , context):
    prompt = f"""
You are a senior software engineer.

Your job is to write or modify code using the given context
Context:
{context}

Task:
{task}

Plan:
{plan}

Instructions:
- Use existing code patterns from context
- Modify existing files instead of rewriting everything
- Generate ONLY the required code for the task
- Do NOT explain anything
- Do NOT add extra features
- Keep code minimal and focused
- Avoid unnecessary imports
- Follow best practices but stay concise
- Return ONLY code (no text, no explanation)

Output format:
CODE ONLY
"""

    return generate_response(prompt)