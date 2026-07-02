# Context-Aware RAG Chatbot

This project is a **Retrieval-Augmented Generation (RAG) based customer support chatbot** built using Python. It uses a local vector database (Chroma), SQLite for user personalization, and Groq LLM (LLaMA 3) for response generation.

---

## 🚀 Features

- RAG-based question answering using company FAQ
- User personalization using SQLite database
- Context-aware responses using Chroma vector store
- Groq API integration (LLaMA 3 model)
- Error handling for invalid users, missing API keys, and missing context
- Terminal-based chatbot interface

---

## 🧰 Tech Stack

- Python 3.10+
- LangChain
- Chroma DB (Vector Store)
- SQLite (User Database)
- HuggingFace Embeddings
- Groq API (llama-3.1-8b-instant)
- dotenv

---

## 📁 Project Structure
context-aware-rag-bot/
│
├── app.py
├── ingest.py
├── create_db.py
├── company_faq.txt
├── users.db
├── chroma_db/
├── requirements.txt
├── README.md
├── .env
├── .env.example


---

## ⚙️ Setup Instructions

### 1. Install dependencies
```bash
pip install -r requirements.txt
2. Create SQLite database
python create_db.py
3. Create vector database
python ingest.py
4. Run chatbot
python app.py
👤 Sample Users
User ID	Name	Membership Tier
101	Riya Sharma	Gold
102	Aman Verma	Silver
103	Neha Iyer	Platinum
💬 Sample Test Cases
Test Case 1

User ID: 101
Question: What is the refund policy?

Test Case 2

User ID: 103
Question: Do I get premium customer support?

Test Case 3

User ID: 999
Question: What are my benefits?

Test Case 4

User ID: 102
Question: Can I cancel my account?

⚠️ Error Handling
Invalid user ID → "User not found. Please enter a valid user_id."
Missing API key → Prompt to set GROQ_API_KEY
No relevant context → "I do not have enough information in the provided knowledge base to answer this."
API failure → Graceful error message instead of crash
📌 Notes
Run create_db.py before starting app
Run ingest.py before starting chatbot
Ensure .env file contains valid Groq API key
🏁 Status

✔ RAG pipeline implemented
✔ SQLite integration completed
✔ Groq API working
✔ Vector DB created using Chroma
✔ Fully functional chatbot ready

👨‍💻 Author

Context-Aware RAG Chatbot Project