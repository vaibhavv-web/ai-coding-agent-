from git import Repo
import os
from dotenv import load_dotenv

load_dotenv()

def push_changes(repo_path, commit_message="AI update"):
    try:
        repo = Repo(repo_path)

        # ✅ Load token from .env file
        token = os.getenv("GITHUB_TOKEN")

        if not token:
            return "❌ Git push failed: GITHUB_TOKEN not found in .env"

        # ✅ Set authenticated remote URL
        origin_url = repo.remotes.origin.url

        if "@" not in origin_url:
            origin_url = origin_url.replace(
                "https://",
                f"https://{token}@"
            )
            repo.remotes.origin.set_url(origin_url)

        # ✅ Add changes
        repo.git.add(A=True)

        # ✅ Only commit if there are actual changes
        if repo.is_dirty(untracked_files=True):
            repo.index.commit(commit_message)
        else:
            return "⚠️ No changes to commit"

        # ✅ Push
        repo.remotes.origin.push()

        return "✅ Changes pushed to GitHub"

    except Exception as e:
        return f"❌ Git push failed: {str(e)}"