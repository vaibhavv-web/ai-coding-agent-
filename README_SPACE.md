---
title: AI Coding Agent
emoji: 🤖
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
---

# 🤖 AI Coding Agent

An intelligent coding assistant that automatically clones GitHub repos, understands codebases, and generates code changes.

## ✨ Features

- 🔍 **Smart Code Analysis** - Uses RAG (Retrieval Augmented Generation) to understand your codebase
- 💻 **Automated Coding** - Generates code based on natural language tasks
- 🚀 **GitHub Integration** - Automatically pushes changes to your repository
- 🧠 **Memory System** - Remembers previous tasks and maintains context
- ✅ **Code Review** - Built-in review phase to ensure quality

## 🛠️ Tech Stack

- **LLM**: Google Gemini 2.5 Flash
- **Vector DB**: ChromaDB for semantic code search
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Framework**: Flask + LangChain
- **Version Control**: GitPython

## 🚀 How to Use

1. **Enter GitHub Repo URL** - Provide the repository you want to modify
2. **Add GitHub Token** - (Optional if set in secrets) For pushing changes
3. **Describe Your Task** - Tell the AI what you want to build in natural language
4. **Watch the Magic** - The AI will:
   - Clone your repo
   - Analyze the codebase
   - Plan the implementation
   - Generate code
   - Push changes to GitHub

## 📋 Example Tasks

- "Add input validation to all functions in utils.py"
- "Create a new authentication module with JWT"
- "Add error handling to the API endpoints"
- "Refactor the database connection code"

## 🎯 Use Cases

- **Rapid Prototyping** - Quickly add features to existing projects
- **Code Refactoring** - Modernize legacy code
- **Bug Fixes** - Automated issue resolution
- **Documentation** - Generate code comments and docs

## 🔒 Privacy & Security

- Your code is processed temporarily and not stored
- GitHub tokens are handled securely
- All operations are logged for transparency

## 👨‍💻 Built by Vaibhav

[GitHub](https://github.com/vaibhavv-web) | [LinkedIn](https://linkedin.com/in/vaibhavv-web)

---

**Note**: This is a demo application. Always review AI-generated code before deploying to production.
