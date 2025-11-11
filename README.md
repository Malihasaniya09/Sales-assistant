🧊 Secure Refrigerator Sales Assistant
📝 Overview

The Secure Refrigerator Sales Assistant is an AI-powered chatbot that helps customers explore refrigerator products interactively.
It integrates Guardrails-AI for secure and structured LLM responses, FAISS for semantic search through product catalogs, and a Streamlit interface for an intuitive user experience.

🚀 Features

🧠 Conversational product recommendations

🔍 FAISS-based semantic search for product retrieval

🛡️ Guardrails-AI validation for safe, accurate responses

🧾 Integration with product catalogs (PDF/CSV)

💻 Streamlit frontend for a user-friendly experience

🧰 Tech Stack
Component	Technology
Frontend	Streamlit
Backend API	FastAPI
AI Validation	Guardrails-AI

📂 Project Structure
sales_assistant/
│

├── .env                        # API keys and environment variables

│

├── api.py                      # Handles API calls and chatbot initialization

├── assist.py                   # Catalog statistics & helper functions

├── fast_api.py                 # Backend server with FastAPI

├── frontend.py                 # Streamlit UI for the chatbot

│
├── product_catalog.pdf         # General product catalog

├── refrigerator_catalog.pdf    # Refrigerator-specific data

│
├── req.txt                     # Required dependencies
└── __pycache__/                # Compiled cache (auto-generated)

Vector Search	FAISS
LLM	OpenAI / Hugging Face Models
Data	Product catalogs (PDF/CSV)
