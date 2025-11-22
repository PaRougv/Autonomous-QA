# 🤖 Autonomous QA Agent for Test Case & Script Generation

An AI-powered **autonomous QA assistant** that understands your project documentation, analyzes a real checkout page, and **automatically generates both structured test cases and runnable Selenium scripts**.

> 🧪 **Upload → 📚 Build Knowledge → 🧠 Generate Test Cases → 💻 Get Selenium Code**

---

## 🎥 Demo Video (Project Explanation)

[![Watch the video](https://img.youtube.com/vi/jNXwsuptiVs/maxresdefault.jpg)](https://www.youtube.com/watch?v=jNXwsuptiVs)

---


## 🚀 Features

- 📥 Upload documentation + HTML (checkout page)
- 🔎 RAG-powered knowledge extraction (grounded in your docs)
- 🧠 AI-generated test cases (ID, feature, scenario, steps, expected result)
- 🐍 One-click **Selenium Python script generation** from a selected test case
- ✅ Positive & ❌ Negative scenarios
- 🔐 Strict JSON structure for reliable parsing
- ⚙️ Scripts designed to be runnable locally

---

## 🏗️ Tech Stack

| Layer      | Technology         |
|------------|--------------------|
| Backend    | **FastAPI**        |
| Frontend   | **Streamlit**      |
| AI Model   | **OpenAI API (LLM)** |
| Embeddings | **Sentence Transformers** |
| Automation | **Selenium + WebDriver Manager** |
| Storage    | Custom vector store using **numpy + pickle** |

---

## 📂 Project Structure

```text
backend/
  main.py           # FastAPI app (API endpoints)
  models.py         # Pydantic models (TestCase, requests, responses)
  rag_engine.py     # RAG pipeline + test-case & script generation logic
  vector_store.py   # Simple in-memory + pickle-based vector store
  llm_client.py     # LLM wrapper (OpenAI client)
  parsers.py        # Support docs & checkout.html parsing

frontend/
  app.py            # Streamlit UI (multi-step workflow)

assets/
  checkout.html          # Sample checkout page under test
  product_specs.md       # Product / pricing rules
  ui_ux_guide.txt        # UI/UX guidelines
  api_endpoints.json     # Example API contract

tests/                   # (You can save generated Selenium scripts here)

requirements.txt
README.md
