from git import Repo
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils import load_code_files, chunk_code
import time 

def clone_repo(repo_url , token):
    path = f"data/repo_{int(time.time())}"

    print("📥 Cloning repository...")
    Repo.clone_from(repo_url, path)

    print("✅ Repo cloned successfully!")
    return path

def create_vector_db(repo_path):
    print("🔄 Loading embedding model...")

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print(" Loading code files...")
    files = load_code_files(repo_path)
    print(f" Total files loaded: {len(files)}")

    if not files:
        raise ValueError(" No files found in repository!")

    all_chunks = []

    print(" Chunking code...")
    for file in files:
        try:
            chunks = chunk_code(file)
            print(f"📄 {file['path']} → {len(chunks)} chunks")
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"⚠️ Error processing {file['path']}: {e}")

    print(f" Total chunks created: {len(all_chunks)}")

    # 🚨 CRITICAL FIX: Prevent empty embeddings crash
    if not all_chunks:
        raise ValueError(" No chunks generated. Check chunk_code or file loading.")

    texts = []
    metadatas = []

    for c in all_chunks:
        content = c.get("content", "").strip()
        path = c.get("path", "unknown")

        # Skip empty content safely
        if not content:
            continue

        texts.append(content)
        metadatas.append({"path": path})

    print(f" Valid chunks for embedding: {len(texts)}")

    if not texts:
        raise ValueError(" No valid text chunks to embed.")

    print(" Creating vector database...")

    vectordb = Chroma.from_texts(
        texts=texts,
        embedding=embedding,
        metadatas=metadatas,
        persist_directory="vectorstore"
    )

    vectordb.persist()

    print(" Vector DB created successfully!")

    return vectordb

def add_numbers(num1, num2):
	return num1 + num2

def add_numbers(num1, num2):
	"""Returns the sum of two numbers"""
	return num1 + num2