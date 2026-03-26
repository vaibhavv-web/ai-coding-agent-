from git import Repo
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils import load_code_files, chunk_code


def clone_repo(repo_url, path="data/repo"):
    if os.path.exists(path):
        return path
    Repo.clone_from(repo_url, path)
    return path


def create_vector_db(repo_path):
    print("🔄 Loading embedding model...")

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("📂 Loading code files...")
    files = load_code_files(repo_path)
    print(f"📂 Total files loaded: {len(files)}")

    all_chunks = []

    print("✂️ Chunking code...")
    for file in files:
        chunks = chunk_code(file)
        all_chunks.extend(chunks)

    print(f"✅ Total chunks created: {len(all_chunks)}")

    texts = [c["content"] for c in all_chunks]
    metadatas = [{"path": c["path"]} for c in all_chunks]

    print("🧠 Creating vector database...")

    vectordb = Chroma.from_texts(
        texts=texts,
        embedding=embedding,
        metadatas=metadatas,
        persist_directory="vectorstore"
    )

    vectordb.persist()

    print("✅ Vector DB created successfully!")

    return vectordb