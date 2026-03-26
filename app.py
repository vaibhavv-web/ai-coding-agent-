from ingest import clone_repo, create_vector_db
from query import query_codebase , generate_answer
import google.generativeai as genai

genai.configure(api_key="your api key")

repo_url = input("Enter GitHub repo URL: ")

repo_path = clone_repo(repo_url)
create_vector_db(repo_path)

while True:
    q = input("\n💬 Ask something: ")

    results = query_codebase(q)

    print("\n📌 Generating Answer...\n")

    answer = generate_answer(q, results)

    print("\n🧠 AI Explanation:\n")
    print(answer)
