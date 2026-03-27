import google.generativeai as genai
from agents.planner import planner_agent
from agents.coder import coder_agent
from ingest import clone_repo, create_vector_db
from agents.reviewer import reviewer_agent
from query import query_codebase

# 🔑 Configure Gemini API
genai.configure(api_key="YOUR_API_KEY_HERE")


# ✅ Input Validation
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


def main():
    repo_url = input("Enter GitHub repo URL: ")

    repo_path = clone_repo(repo_url)
    create_vector_db(repo_path)

    while True:
        task = input("\n💬 Enter your task: ")

        if not is_valid_task(task):
            print("\n Invalid task. Please enter a meaningful development task.\n")
            continue

        # =========================
        # 🧠 PLANNING
        # =========================
        print("\n==============================")
        print("🧠 PLANNING PHASE")
        print("==============================\n")

        print("\n Fetching relavant code context..\n")

        context_results= query_codebase(task)
        context = ""
        for r in context_results: 
            context += f"\nFile: {r['file']}\n{r['content']}\n"

        print("context loaded\n")

        plan = planner_agent(task , context)

        print(plan)

        # =========================
        # 💻 CODING
        # =========================
        print("\n==============================")
        print("💻 CODING PHASE")
        print("==============================\n")

        code = coder_agent(task, plan , context)
        print(code)

        # =========================
        # 🔍 REVIEW LOOP
        # =========================
        print("\n==============================")
        print("🔍 REVIEW PHASE")
        print("==============================\n")

        MAX_ITERATIONS = 5
        QUALITY_THRESHOLD = 8

        iteration = 0

        while iteration < MAX_ITERATIONS:
            print(f"\n🔍 Review Iteration {iteration + 1}...\n")

            review = reviewer_agent(task, code , context)

            score = review.get("score", 5)
            improved_code = review.get("code", code)

            print(f"⭐ Score: {score}")

            # ✅ Stop if good enough
            if score >= QUALITY_THRESHOLD:
                print("\n✅ Code is good enough. Stopping improvements.\n")
                break

            # ✅ Stop if no improvement
            if improved_code.strip() == code.strip():
                print("\n⚠️ No further improvements detected. Stopping.\n")
                break

            # 🔁 Improve
            print("♻️ Reviewer suggested improvements. Updating code...\n")
            code = improved_code

            iteration += 1

        # Safety stop
        if iteration == MAX_ITERATIONS:
            print("\n⚠️ Max iterations reached. Returning best version.\n")

        # =========================
        # ✅ FINAL OUTPUT
        # =========================
        print("\n==============================")
        print("🚀 FINAL CODE")
        print("==============================\n")

        print(code)

        input("\n👉 Press ENTER to continue...\n")


if __name__ == "__main__":
    main()