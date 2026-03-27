from llm import generate_response



def planner_agent(task , context):
    prompt = f"""
You are a senior software architect.

Your job is to create a concise execution plan using the given codebase context 

Context:
{context}

Task:
{task}

Rules :
- Generate ONLY the required explanation for the task
- Do not explain everything 
- Be structured
- Keep steps logical
- Focus on implementation
- Return numbered steps
- Use existing files and structure if possible
- Do NOT suggest rewriting entire systems

Output Structure : 
1. Step one 
2. Step two
3. Step three

Return ONLY the steps 
"""


    return generate_response(prompt)