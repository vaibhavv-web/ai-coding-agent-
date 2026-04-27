import json
import os
from datetime import datetime

MEMORY_DIR = "memory"
os.makedirs(MEMORY_DIR, exist_ok=True)

def get_memory_file(repo_url):
    # Create unique file per repo
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    return os.path.join(MEMORY_DIR, f"{repo_name}_memory.json")

def load_memory(repo_url):
    memory_file = get_memory_file(repo_url)
    if os.path.exists(memory_file):
        with open(memory_file, "r") as f:
            return json.load(f)
    return {
        "repo_url": repo_url,
        "tasks_done": [],
        "files_edited": [],
        "functions_known": [],
        "errors_encountered": []
    }

def save_memory(repo_url, memory):
    memory_file = get_memory_file(repo_url)
    with open(memory_file, "w") as f:
        json.dump(memory, f, indent=2)

def add_task(repo_url, task, files_changed):
    memory = load_memory(repo_url)
    memory["tasks_done"].append({
        "task": task,
        "files": files_changed,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    # Keep last 20 tasks only
    memory["tasks_done"] = memory["tasks_done"][-20:]
    save_memory(repo_url, memory)

def add_edited_file(repo_url, file_path, action):
    memory = load_memory(repo_url)
    entry = {"file": file_path, "action": action,
             "time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    # Avoid duplicates
    memory["files_edited"] = [
        f for f in memory["files_edited"] if f["file"] != file_path
    ]
    memory["files_edited"].append(entry)
    save_memory(repo_url, memory)

def add_error(repo_url, error, task):
    memory = load_memory(repo_url)
    memory["errors_encountered"].append({
        "error": error,
        "task": task,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    # Keep last 10 errors only
    memory["errors_encountered"] = memory["errors_encountered"][-10:]
    save_memory(repo_url, memory)

def add_function(repo_url, function_name, file_path):
    memory = load_memory(repo_url)
    entry = {"function": function_name, "file": file_path}
    if entry not in memory["functions_known"]:
        memory["functions_known"].append(entry)
    save_memory(repo_url, memory)

def get_memory_summary(repo_url):
    memory = load_memory(repo_url)
    
    summary = "=== MEMORY SUMMARY ===\n"
    
    if memory["tasks_done"]:
        summary += "\nPrevious Tasks:\n"
        for t in memory["tasks_done"][-5:]:  # last 5
            summary += f"  - {t['task']} ({t['time']})\n"
    
    if memory["files_edited"]:
        summary += "\nFiles Edited:\n"
        for f in memory["files_edited"][-5:]:
            summary += f"  - {f['file']} ({f['action']})\n"
    
    if memory["errors_encountered"]:
        summary += "\nPast Errors:\n"
        for e in memory["errors_encountered"][-3:]:
            summary += f"  - {e['error']} while: {e['task']}\n"

    if memory["functions_known"]:
        summary += "\nKnown Functions:\n"
        for fn in memory["functions_known"][-10:]:
            summary += f"  - {fn['function']} in {fn['file']}\n"

    return summary