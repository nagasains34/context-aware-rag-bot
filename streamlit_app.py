import os
import sqlite3

import streamlit as st
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------- CONFIG ----------------
st.set_page_config(page_title="NovaCart Support Bot", page_icon="🛒")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))

if not GROQ_API_KEY:
    st.error(
        "GROQ_API_KEY is not set. Add it under Settings → Secrets "
        "(Streamlit Cloud) as GROQ_API_KEY = \"your-key\"."
    )
    st.stop()


# ---------------- ONE-TIME SETUP (cached) ----------------
@st.cache_resource(show_spinner="Setting up user database...")
def init_users_db():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            membership_tier TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        INSERT OR REPLACE INTO users (user_id, name, membership_tier)
        VALUES
        (101, 'Riya Sharma', 'Gold'),
        (102, 'Aman Verma', 'Silver'),
        (103, 'Neha Iyer', 'Platinum')
        """
    )
    conn.commit()
    return conn


@st.cache_resource(show_spinner="Loading knowledge base...")
def init_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    if not os.path.isdir("chroma_db"):
        loader = TextLoader("company_faq.txt", encoding="utf-8")
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)
        vectorstore = Chroma.from_documents(
            documents=chunks, embedding=embeddings, persist_directory="chroma_db"
        )
    else:
        vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)

    return vectorstore.as_retriever(search_kwargs={"k": 3})


@st.cache_resource(show_spinner=False)
def init_llm():
    return ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant")


def get_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT name, membership_tier FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        return {"name": result[0], "membership_tier": result[1]}
    return None


conn = init_users_db()
retriever = init_vectorstore()
llm = init_llm()

# ---------------- SIDEBAR: LOGIN ----------------
st.sidebar.title("👤 NovaCart Login")
user_id_input = st.sidebar.text_input("Enter your User ID", value="101")

user = None
if user_id_input.strip().isdigit():
    user = get_user(conn, int(user_id_input.strip()))
    if user:
        st.sidebar.success(f"Logged in as {user['name']} ({user['membership_tier']})")
    else:
        st.sidebar.error("User not found.")
elif user_id_input.strip():
    st.sidebar.error("User ID must be a number.")

st.sidebar.markdown("---")
st.sidebar.caption("Sample IDs: 101 (Gold), 102 (Silver), 103 (Platinum)")

# ---------------- MAIN CHAT ----------------
st.title("🛒 NovaCart Support Assistant")
st.caption("Ask about refunds, delivery, membership benefits, and more.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("Type your question here...")

if query:
    if not user:
        st.error("Please enter a valid User ID in the sidebar before asking a question.")
    else:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        docs = retriever.invoke(query)

        if not docs:
            answer = "I do not have enough information in the provided knowledge base to answer this."
        else:
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
                answer = response.content
            except Exception as e:
                answer = f"API Error: {str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)
