import os

def load_code_files(repo_path):
    import os

    code_files = []

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith((
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".json", ".md", ".txt", ".yaml", ".yml"
)):
                full_path = os.path.join(root, file)

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if content.strip():  # skip empty files
                        code_files.append({
                            "path": full_path,
                            "content": content
                        })

                except Exception as e:
                    print(f" Failed to read {full_path}: {e}")

    return code_files

def chunk_code(file, chunk_size=100, overlap=20):
    lines = file["content"].split("\n")
    chunks = []

    if not lines:
        return []

    step = max(1, chunk_size - overlap)

    for i in range(0, len(lines), step):
        chunk = "\n".join(lines[i:i + chunk_size])

        if not chunk.strip():
            continue

        chunks.append({
            "content": chunk,
            "path": file["path"]
        })

    return chunks

def add(a, b):
	return a + b

def add(a, b):
    if isinstance(a, float) or isinstance(b, float):
        return float(a) + float(b)
    else:
        return a + b

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    max_divisor = int(n**0.5) + 1
    for d in range(3, max_divisor, 2):
        if n % d == 0:
            return False
    return True