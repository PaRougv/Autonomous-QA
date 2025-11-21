# Autonomous QA Agent for Test Case & Script Generation

This project implements an intelligent, autonomous QA agent that:

- Builds a **testing brain** (knowledge base) from project documentation and the target HTML page.
- Generates **test cases** grounded strictly in the provided documents.
- Generates **Selenium Python scripts** for selected test cases.

Backend: **FastAPI**  
Frontend: **Streamlit**  

---

## Project Structure

```text
backend/
  main.py           # FastAPI app
  models.py         # Pydantic models
  rag_engine.py     # RAG pipeline + agents
  vector_store.py   # Simple vector DB using numpy + pickle
  llm_client.py     # LLM wrapper (OpenAI)
  parsers.py        # Document + HTML parsers

frontend/
  app.py            # Streamlit UI

assets/
  checkout.html
  product_specs.md
  ui_ux_guide.txt
  api_endpoints.json

requirements.txt
README.md
