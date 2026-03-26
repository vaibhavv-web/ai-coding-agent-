from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import google.generativeai as genai


def query_codebase(question):
    print("\n🔍 Searching for relevant code...\n")

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma(
        persist_directory="vectorstore",
        embedding_function=embedding
    )

    # 🔥 get top 5 relevant chunks
    docs = vectordb.similarity_search(question, k=5)

    results = []

    for i, doc in enumerate(docs, 1):
        results.append({
            "rank": i,
            "content": doc.page_content,
            "file": doc.metadata.get("path", "Unknown")
        })

    return results


def generate_answer(question, results):
    context = ""

    for r in results:
        context += f"\nFile: {r['file']}\n{r['content']}\n"

    prompt = f"""
You are a senior software engineer.

Answer the question based on the code context below.

Question:
{question}

Code Context:
{context}

Instructions:
- Explain clearly
- Mention file names
- Keep it concise but useful
"""

    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content(prompt)

    return response.text