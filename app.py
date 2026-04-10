import json
import os
import re
from git_utils import push_changes
from dotenv import load_dotenv
from agents.planner import planner_agent
from agents.coder import coder_agent
from ingest import clone_repo, create_vector_db
from agents.reviewer import reviewer_agent
from query import query_codebase
from file_editor import write_file, create_file
from file_editor import smart_modify_file
from git import Repo
load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")


# =========================
#  Clean JSON Output
# =========================
def clean_json_output(text):
    if not isinstance(text, str):
        return ""

    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return text


# =========================
#  Robust JSON Extractor
# =========================


def extract_json(text):
    def sanitize_code_value(m):
        inner = m.group(1)
        # Fix triple quotes -> escaped single quotes
        inner = inner.replace('"""', "\\'\\'\\'")
        inner = inner.replace("'''", "\\'\\'\\'")
        return '"code": "' + inner + '"'
    
    # Step 1: Strip markdown fences
    text = re.sub(r"```(?:json)?", "", text).strip().strip("`").strip()

    # Step 2: Anchor on "files" key
    files_idx = text.find('"files"')
    if files_idx == -1:
        print("❌ No JSON found")
        return None

    start = text.rfind('{', 0, files_idx)
    if start == -1:
        print("❌ No opening brace found")
        return None

    # Step 3: Try json.JSONDecoder which handles nesting correctly
    decoder = json.JSONDecoder()
    try:
        obj, _ = decoder.raw_decode(text, start)
        return obj
    except json.JSONDecodeError:
        pass

    # Step 4: Fix unescaped real newlines/tabs inside strings, then retry
    # We need to sanitize ONLY inside string values
    raw = text[start:]
    result = []
    in_string = False
    i = 0
    while i < len(raw):
        ch = raw[i]

        if ch == '\\' and i + 1 < len(raw):
            # Already escaped — keep as-is
            result.append(ch)
            result.append(raw[i+1])
            i += 2
            continue

        if ch == '"':
            in_string = not in_string
            result.append(ch)
            i += 1
            continue

        if in_string:
            if ch == '\n':
                result.append('\\n')
            elif ch == '\r':
                result.append('\\r')
            elif ch == '\t':
                result.append('\\t')
            else:
                result.append(ch)
        else:
            result.append(ch)
        i += 1

    fixed = ''.join(result)

    try:
        obj, _ = decoder.raw_decode(fixed, 0)
        return obj
    except json.JSONDecodeError as e:
        print("❌ FINAL JSON PARSE FAILED:", e)
        print("\n🔴 RAW OUTPUT:\n", fixed[:500])
        return None
# =========================
# Input Validation
# =========================
def is_valid_task(task):
    task = task.strip()

    if not task:
        return False
    if len(task) < 5:
        return False
    if task.isdigit():
        return False
    if "http://" in task or "https://" in task:
        return False

    return True


# =========================
#  File Safety
# =========================
def is_safe_file(file_path):
    if not isinstance(file_path, str):
        return False

    if not file_path.endswith(".py"):
        return False

    blocked = ["../", "__pycache__", ".env"]
    for b in blocked:
        if b in file_path:
            return False

    return True


# =========================
#  MAIN
# =========================
def main():
    repo_url = input("Enter GitHub repo URL: ")

    repo_path = clone_repo(repo_url , TOKEN)
    create_vector_db(repo_path)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    while True:
        task = input("\n Enter your task: ")

        if not is_valid_task(task):
            print("\n Invalid task\n")
            continue

        # =========================
        #  PLANNING
        # =========================
        print("\n PLANNING PHASE\n")

        context_results = query_codebase(task)
        context = ""

        for r in context_results:
            context += f"\nFile: {r['file']}\n{r['content']}\n"

        plan = planner_agent(task, context)
        print(plan)

        # =========================
        # 💻 CODING
        # =========================
        print("\n CODING PHASE\n")

        code = coder_agent(task, plan, context)

        print("\n================ RAW LLM OUTPUT ================\n")
        print(code)
        print("\n==============================================\n")

       

        parsed = extract_json(code)

        if not parsed:
            print(" Failed to parse JSON")
            continue

        files = parsed.get("files", []) 

        

        # =========================
        #  APPLY CHANGES
        # =========================
        print("\n APPLYING CHANGES\n")

        for file_obj in files:
            relative_path = file_obj.get("file")
            action = file_obj.get("action")
            new_code = file_obj.get("code")

            if not relative_path or not action or not new_code:
                print(" Skipping invalid entry")
                continue

            if not is_safe_file(relative_path):
                print(f" Unsafe file blocked: {relative_path}")
                continue

            file_path = os.path.join(BASE_DIR, relative_path)

            print(" Writing to:", file_path)

            if action == "create":
                result = create_file(file_path, new_code)

            target = file_obj.get("target")
            if action == "modify":
                if target:
                    result = smart_modify_file(file_path , target , new_code)
                else:
                    result = write_file(file_path , new_code)


            
            else:
                result = "Unknown action"

            print(f" {result}")

         
        repo = Repo(repo_path)
        print("Remote URL:" , repo.remotes.origin.url)

        
        print("\n🚀 Pushing changes to GitHub...")
        result = push_changes(repo_path , f"AI Update: {task}")
        print(result)

       
        # =========================
        #  REVIEW LOOP (SAFE)
        # =========================
        print("\n REVIEW PHASE\n")

        MAX_ITERATIONS = 3
        QUALITY_THRESHOLD = 8

        iteration = 0

        while iteration < MAX_ITERATIONS:
            review = reviewer_agent(task, code, context)

            if not isinstance(review, dict):
                print(" Invalid review response")
                break

            score = review.get("score", 5)
            improved_code = review.get("code", code)

            print(f" Score: {score}")

            if score >= QUALITY_THRESHOLD:
                print(" Code is good enough")
                break

            if improved_code.strip() == code.strip():
                print(" No improvement detected")
                break

            code = improved_code
            iteration += 1

        # =========================
        #  FINAL OUTPUT
        # =========================
        print("\n FINAL RESPONSE\n")
        print(code)

        input("\nPress ENTER to continue...\n")


if __name__ == "__main__":
    main()