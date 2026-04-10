import time
from git import Repo 
import os

def clone_repo(repo_url , token):
    path = f"data/repo_{int(time.time())}"
    
    repo_url = repo_url.replace(
        "https://",
        f"https://{token}@"
    )

    Repo.clone_from(repo_url , path)

    return path

    print("📥 Cloning repository...")
    Repo.clone_from(repo_url, path)

    print("✅ Repo cloned successfully!")
    return path

def add(num1, num2):
    return num1 + num2

def multiply(num1, num2):
    return num1 * num2