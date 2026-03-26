import os

def load_code_files(repo_path):
    code_files = []

    allowed_extensions = (
        ".py", ".js", ".ts", ".java",
        ".md", ".json", ".txt",
        ".yaml", ".yml",
        ".html", ".css", ".jsx", ".tsx"
    )

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(allowed_extensions):

                full_path = os.path.join(root, file)

                # ❌ skip junk folders
                if any(x in full_path for x in [
                    "__pycache__", ".git", "node_modules", ".venv"
                ]):
                    continue

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()

                        # skip empty files
                        if len(code.strip()) < 20:
                            continue

                        code_files.append({
                            "content": code,
                            "path": full_path
                        })

                except Exception as e:
                    print("Error reading:", full_path)

    return code_files
def chunk_code(file):
    lines = file["content"].split("\n")
    chunks = []

    chunk_size = 20   # 🔥 smaller chunks
    overlap = 5

    for i in range(0, len(lines), chunk_size - overlap):
        chunk = "\n".join(lines[i:i + chunk_size])

        if len(chunk.strip()) < 5:
            continue

        chunks.append({
            "content": chunk,
            "path": file["path"]
        })

    return chunks