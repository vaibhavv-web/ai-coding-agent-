from llm import generate_response


def planner_agent(task, context):
    prompt = f"""
You are a senior software architect.

Your job is to break down the task into clear implementation steps.

TASK:
{task}

CONTEXT:
{context}

Return clear step-by-step plan.
"""

    return generate_response(prompt)