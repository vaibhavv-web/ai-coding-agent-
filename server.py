from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import os
import re
import queue
import threading
from git_utils import push_changes
from dotenv import load_dotenv
from agents.planner import planner_agent
from agents.coder import coder_agent
from flask import Flask , render_template
from ingest import create_vector_db
from clone import clone_repo
from agents.reviewer import reviewer_agent
from query import query_codebase
from file_editor import write_file, create_file, smart_modify_file
from git import Repo
from llm import get_last_llm_error
from memory.memory_manager import (
    load_memory, add_task, add_edited_file,
    add_error, get_memory_summary
)

load_dotenv()

token = os.getenv("GITHUB_TOKEN")
print("TOKEN LOADED:", token)

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

log_queues = {}



def get_queue(session_id):
    if session_id not in log_queues:
        log_queues[session_id] = queue.Queue()
    return log_queues[session_id]


def send_log(q, message, type="info"):
    q.put(json.dumps({"type": "log", "message": message, "level": type}))


def send_phase(q, phase):
    q.put(json.dumps({"type": "phase", "phase": phase}))


def send_file(q, filename, action):
    q.put(json.dumps({"type": "file", "filename": filename, "action": action}))


def send_status(q, status, message=""):
    q.put(json.dumps({"type": "status", "status": status, "message": message}))


def send_stats(q, tasks, files, pushes):
    q.put(json.dumps({"type": "stats", "tasks": tasks, "files": files, "pushes": pushes}))


def send_memory(q, memory_data):
    q.put(json.dumps({"type": "memory", "data": memory_data}))


def send_done(q):
    q.put(json.dumps({"type": "done"}))


def extract_json(text):
    text = re.sub(r"```(?:json)?", "", text).strip().strip("`").strip()
    files_idx = text.find('"files"')
    if files_idx == -1:
        return None
    start = text.rfind('{', 0, files_idx)
    if start == -1:
        return None
    decoder = json.JSONDecoder()
    try:
        obj, _ = decoder.raw_decode(text, start)
        return obj
    except json.JSONDecodeError:
        pass
    raw = text[start:]
    result = []
    in_string = False
    i = 0
    while i < len(raw):
        ch = raw[i]
        if ch == '\\' and i + 1 < len(raw):
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
            elif ch == '\\' and i + 1 < len(raw):
                next_ch = raw[i + 1]
                if next_ch not in ('"', '\\', '/', 'n', 'r', 't', 'b', 'f', 'u'):
                    result.append('\\\\')
                    result.append(next_ch)
                else:
                    result.append(ch)
                    result.append(next_ch)
                i += 2
                continue
            else:
                result.append(ch)
        else:
            result.append(ch)
        i += 1
    fixed = ''.join(result)
    try:
        obj, _ = decoder.raw_decode(fixed, 0)
        return obj
    except json.JSONDecodeError:
        return None


def is_safe_file(file_path):
    if not isinstance(file_path, str):
        return False
    normalized = file_path.replace("\\", "/")
    if normalized.startswith("/") or ":" in normalized or ".." in normalized:
        return False
    allowed_extensions = {
        ".py", ".js", ".jsx", ".ts", ".tsx", ".html",
        ".css", ".scss", ".json", ".md", ".yml", ".yaml", ".txt"
    }
    if not any(normalized.endswith(ext) for ext in allowed_extensions):
        return False
    blocked = ["__pycache__", ".env"]
    for b in blocked:
        if b in file_path:
            return False
    return True


def run_agent_task(session_id, repo_url, token, task):
    q = get_queue(session_id)
    import time 
    time.sleep(1)
    stats = {"tasks": 0, "files": 0, "pushes": 0}

    try:
        # CLONE PHASE
        send_phase(q, "clone")
        send_log(q, f"📥 Cloning repository: {repo_url}", "info")
        
        try:
            repo_path = clone_repo(repo_url, token)
            send_log(q, "✅ Repository cloned successfully!", "success")
        except Exception as clone_err:
            send_log(q, f"❌ Clone failed: {str(clone_err)}", "error")
            send_status(q, "error", f"Clone failed: {str(clone_err)}")
            send_done(q)
            return

        try:
            send_log(q, "🔄 Loading embedding model...", "info")
            create_vector_db(repo_path)
            send_log(q, "✅ Vector DB created!", "success")
        except Exception as db_err:
            send_log(q, f"❌ Vector DB failed: {str(db_err)}", "error")
            send_status(q, "error", f"Vector DB failed: {str(db_err)}")
            send_done(q)
            return
        # Load memory
        memory_summary = get_memory_summary(repo_url)
        if memory_summary.strip() != "=== MEMORY SUMMARY ===":
            send_log(q, "🧠 Memory loaded from previous sessions", "info")

        # PLAN PHASE
        send_phase(q, "plan")
        send_log(q, "", "muted")
        send_log(q, "══════════ PLANNING PHASE ══════════", "info")
        send_log(q, f"Task: {task}", "")

        context_results = query_codebase(task)
        context = ""
        for r in context_results:
            context += f"\nFile: {r['file']}\n{r['content']}\n"

        plan = planner_agent(task, context, memory_summary)
        send_log(q, "✅ Plan generated successfully", "success")

        # CODE PHASE
        send_phase(q, "code")
        send_log(q, "", "muted")
        send_log(q, "══════════ CODING PHASE ══════════", "info")
        send_log(q, "Running coder agent (Gemini JSON v2)...", "info")

        code = coder_agent(task, plan, context)
        send_log(q, "✅ Code generated", "success")

        if isinstance(code, dict):
            parsed = code
        else:
            parsed = extract_json(code)
        if not parsed:
            llm_error = get_last_llm_error()
            if llm_error:
                send_log(q, f"LLM error: {llm_error}", "error")
            if isinstance(code, str) and code.strip():
                send_log(q, f"Raw model output preview: {code[:500]}", "warning")
            send_log(q, "❌ Failed to parse JSON from LLM output", "error")
            send_status(q, "error", "Failed to parse code")
            send_done(q)
            return

        files = parsed.get("files", [])

        # APPLY CHANGES
        send_log(q, "", "muted")
        send_log(q, "══════════ APPLYING CHANGES ══════════", "info")

        files_changed = []
        for file_obj in files:
            relative_path = file_obj.get("file")
            action = file_obj.get("action")
            new_code = file_obj.get("code")

            if not relative_path or not action or not new_code:
                send_log(q, "⚠ Skipping invalid entry", "warning")
                continue

            if not is_safe_file(relative_path):
                send_log(q, f"🚫 Unsafe file blocked: {relative_path}", "warning")
                continue

            file_path = os.path.join(repo_path, relative_path)
            send_log(q, f"Writing to: {file_path}", "")

            if action == "create":
                result = create_file(file_path, new_code)
            elif action == "modify":
                target = file_obj.get("target")
                if target:
                    result = smart_modify_file(file_path, target, new_code)
                else:
                    result = write_file(file_path, new_code)
            else:
                result = "Unknown action"

            result_text = str(result)
            level = "warning" if "error" in result_text.lower() or "unknown" in result_text.lower() else "success"
            send_log(q, result_text, level)
            send_file(q, relative_path, action)

            add_edited_file(repo_url, relative_path, action)
            files_changed.append(relative_path)
            stats["files"] += 1

        # PUSH PHASE
        send_phase(q, "push")
        send_log(q, "", "muted")
        send_log(q, "🚀 Pushing changes to GitHub...", "info")

        push_result = push_changes(repo_path, token, f"AI Update: {task}")
        send_log(q, push_result, "success" if "✅" in push_result else "error")

        if "✅" in push_result:
            stats["pushes"] += 1
            send_status(q, "success", push_result)
        else:
            send_status(q, "error", push_result)
            add_error(repo_url, push_result, task)

        # Save memory
        add_task(repo_url, task, files_changed)
        stats["tasks"] += 1

        # Load updated memory
        memory = load_memory(repo_url)
        send_memory(q, {
            "tasks_done": memory.get("tasks_done", []),
            "files_edited": memory.get("files_edited", []),
            "errors_encountered": memory.get("errors_encountered", [])
        })

        send_stats(q, stats["tasks"], stats["files"], stats["pushes"])

        # REVIEW
        send_log(q, "", "muted")
        send_log(q, "══════════ REVIEW PHASE ══════════", "info")

        MAX_ITERATIONS = 2
        QUALITY_THRESHOLD = 8
        iteration = 0

        while iteration < MAX_ITERATIONS:
            review = reviewer_agent(task, code, context)
            if not isinstance(review, dict):
                send_log(q, "⚠ Invalid review response", "warning")
                break
            score = review.get("score", 5)
            send_log(q, f"Score: {score}/10", "info")
            if score >= QUALITY_THRESHOLD:
                send_log(q, "✅ Code quality is good!", "success")
                break
            improved_code = review.get("code", code)
            if improved_code.strip() == code.strip():
                send_log(q, "No improvement detected", "muted")
                break
            code = improved_code
            iteration += 1

        send_log(q, "", "muted")
        send_log(q, "✅ Agent task complete!", "success")

    except Exception as e:
        send_log(q, f"❌ Error: {str(e)}", "error")
        send_status(q, "error", str(e))

    send_done(q)


@app.route("/run", methods=["POST"])
def run():
    data = request.json
    repo_url = data.get("repo_url", "").strip()
    token = data.get("token", "").strip() or os.getenv("GITHUB_TOKEN", "")
    task = data.get("task", "").strip()
    session_id = data.get("session_id", "default")

    if not repo_url or not task:
        return jsonify({"error": "repo_url and task are required"}), 400

    # ✅ Pre-create the queue BEFORE starting thread
    # so messages are never lost
    q = get_queue(session_id)

    t = threading.Thread(
        target=run_agent_task,
        args=(session_id, repo_url, token, task)
    )
    t.daemon = True
    t.start()

    return jsonify({"status": "started", "session_id": session_id})


@app.route("/stream/<session_id>")
def stream(session_id):
    def generate():
        q = get_queue(session_id)
        while True:
            try:
                msg = q.get(timeout=60)
                yield f"data: {msg}\n\n"
                if json.loads(msg).get("type") == "done":
                    break
            except queue.Empty:
                yield "data: {\"type\": \"ping\"}\n\n"

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/memory", methods=["GET"])
def get_memory():
    repo_url = request.args.get("repo_url", "")
    if not repo_url:
        return jsonify({"error": "repo_url required"}), 400
    memory = load_memory(repo_url)
    return jsonify(memory)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False, port=8000, threaded=True)
