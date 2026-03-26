## 🚀 Day 1: Codebase Intelligence using RAG + LLM

### 📌 Overview
Built a Retrieval-Augmented Generation (RAG) system that can understand and answer questions about any codebase.

This system allows users to input a GitHub repository and ask questions in natural language. The system retrieves relevant code snippets and generates intelligent explanations using an LLM.

---

### ⚙️ Features

- 🔗 Clone and process any GitHub repository  
- 📂 Intelligent code file extraction (multi-language support)  
- ✂️ Code chunking for better context understanding  
- 🧠 Semantic embeddings using HuggingFace  
- 🗂️ Vector storage using ChromaDB  
- 🔍 Similarity-based code retrieval  
- 🤖 LLM-powered explanation (Gemini API)  

---

### 🧠 Architecture

1. **Repository Ingestion**  
   → Clone GitHub repo  

2. **Code Processing**  
   → Extract and chunk code files  

3. **Embedding Generation**  
   → Convert code chunks into vector representations  

4. **Vector Database**  
   → Store embeddings in ChromaDB  

5. **Query System**  
   → Retrieve relevant code using semantic search  

6. **LLM Layer**  
   → Generate human-like explanations  

---

