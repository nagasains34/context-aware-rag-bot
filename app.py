import os
import sqlite3

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

# ---------------- LOAD ENV ----------------
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    print("Error: Please set GROQ_API_KEY in the .env file.")
    exit()


# ---------------- SQLITE ----------------
def get_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, membership_tier FROM users WHERE user_id=?",
        (user_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "name": result[0],
            "membership_tier": result[1]
        }
    return None


# ---------------- VECTOR DB ----------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


# ---------------- GROQ LLM ----------------
llm = ChatGroq(
    api_key=groq_api_key,
    model="llama-3.1-8b-instant"
)

# ---------------- CHAT LOOP ----------------
while True:
    user_id = input("\nEnter user_id (or type exit): ")

    if user_id.lower() == "exit":
        break

    if not user_id.isdigit():
        print("Invalid user_id")
        continue

    user = get_user(int(user_id))

    if not user:
        print("User not found. Please enter a valid user_id.")
        continue

    query = input("Enter your question: ")
    
    docs = retriever.invoke(query)

    if not docs:
        print("I do not have enough information in the provided knowledge base to answer this.")
        continue

    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
You are an AI customer support assistant.

You are speaking with:
Name: {user['name']}
Membership Tier: {user['membership_tier']}

IMPORTANT:
Always personalize the answer using the user's name and membership tier when relevant.

Answer the user's question using only the context below.

If the answer is not available in the context, say:
"I do not have enough information in the provided knowledge base to answer this."

Context:
{context}

User Question:
{query}

Answer:
"""

    try:
        response = llm.invoke(prompt)
        print("\n--- ANSWER ---")
        print(response.content)

    except Exception as e:
        print("API Error:", str(e))