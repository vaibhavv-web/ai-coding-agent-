from llm import generate_response
import json


def coder_agent(task, plan, context):
    prompt = f"""
You are a strict backend coding agent.

CRITICAL RULES:
- Output ONLY valid JSON
- NO explanation
- NO markdown
- NO text outside JSON
- NEVER include full file content unless required
# Add this to the end of your prompt in coder.py

STRICT RULES FOR JSON OUTPUT:
1. The entire response must be ONLY a JSON object - nothing else
2. All code goes in the "code" field as a single string
3. Use \\n for newlines in code
4. Use \\t for tabs in code  
5. NEVER use triple quotes inside code strings - use single quotes instead
6. NEVER use unescaped double quotes inside "code" - escape them as \\"
7. f-strings with double quotes must be written as: f\\'...\\' or rewritten to avoid quotes


VERY IMPORTANT:
- NEVER include full file content unless required
- keep code minimal 
- Return MULTIPLE files
- "files" must be a list
- Escape all newlines using \\n
- Each file must contain:
  - file (string)
  - action (create/modify)
  - code (string with \\n)
- Always generate COMPLETE code (functions/classes), not just function calls
- "\n\nCRITICAL: In the JSON output, ALL newlines inside code strings MUST be written as \\n (two characters: backslash + n). NEVER use real newline characters inside JSON strings. Example: \"code\": \"def foo():\\n    return 1\"
RETURN FORMAT(STRICT JSON ONLY , NO EXTRA LINE OUTSIDE):

- for modify:
          - include "target"(function/class name)
          - ONLY return that function code 
          - Do not return full files unless action = create 
{{
  "files": [
    {{
      "file": "utils.py",
      "action": "create/modify/patch",
      "target": "def add",
      "code": "def add(a,b):\\n    return a+b"
    }}
  ]
}}

TASK:
{task}

PLAN:
{plan}

CONTEXT:
{context}
"""

    response = generate_response(prompt)

    if not response or not isinstance(response, str):
        print(" coder_agent: Empty or invalid LLM response")
        return ""

    return response.strip()