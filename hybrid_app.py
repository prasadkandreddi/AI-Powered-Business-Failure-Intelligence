
import os
import json
import streamlit as st

from rank_bm25 import BM25Okapi
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

# =========================
# CONFIG
# =========================

load_dotenv()

st.set_page_config(
    page_title="FailureGPT",
    page_icon="🎯",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>

.main .block-container{
    max-width:1100px;
    padding-top:1rem;
}

.stChatMessage{
    border-radius:15px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# SESSION
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []


# SIDEBAR

with st.sidebar:

    st.title("🎯 FailureGPT")

    st.caption("Business Failure Intelligence")

    st.divider()

    st.markdown("### Popular Cases")

    st.markdown("""
    • Quibi

    • Google Glass

    • Fire Phone

    • Pets.com

    • Google Allo
    """)
    

# HEADER

st.title("AI-Powered Business Failure Intelligence")

st.caption(
    "Analyze startup failures and business mistakes using Hybrid RAG"
)
# LOAD EMBEDDINGS

@st.cache_resource
def load_embeddings():

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

embeddings = load_embeddings()


# LOAD FAISS


@st.cache_resource
def load_vector_db():

    return FAISS.load_local(
        "vector_db",
        embeddings,
        allow_dangerous_deserialization=True
    )

vector_db = load_vector_db()

# LOAD DOCUMENTS

@st.cache_resource
def load_documents():

    docs = []

    dataset_folder = "datasets"

    for file in os.listdir(dataset_folder):

        if file.endswith(".json"):

            try:

                with open(
                    os.path.join(dataset_folder, file),
                    "r",
                    encoding="utf-8"
                ) as f:

                    data = json.load(f)

                    docs.append(
                        data.get("content", "")
                    )

            except:
                pass

    return docs

documents = load_documents()

# BM25

tokenized_docs = [
    doc.lower().split()
    for doc in documents
]

bm25 = BM25Okapi(tokenized_docs)

# GEMINI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

# DISPLAY CHAT

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# HYBRID RAG

def hybrid_rag(query):

    # FAISS

    faiss_docs = vector_db.similarity_search(
        query,
        k=4
    )

    faiss_texts = [
        d.page_content
        for d in faiss_docs
    ]

    # BM25

    bm25_results = bm25.get_top_n(
        query.lower().split(),
        documents,
        n=4
    )

    # MERGE

    combined = []

    for doc in faiss_texts:

        if doc not in combined:
            combined.append(doc)

    for doc in bm25_results:

        if doc not in combined:
            combined.append(doc)

    context = "\n\n".join(
        combined[:8]
    )

    prompt = f"""
You are FailureGPT.

Use ONLY the context provided.

Context:
{context}

Question:
{query}

Instructions:

- Answer directly.
- Keep response concise.
- Use markdown.
- Do NOT generate long essays.
- Maximum 500 words.

Format:

## Summary

## Key Reasons

## Lessons

## Similar Cases
"""

    response = llm.invoke(prompt)

    return response.content

# CHAT INPUT
query = st.chat_input(
    "Ask about startup failures..."
)

if query:

    st.session_state.history.append(query)

    st.session_state.messages.append(
        {
            "role":"user",
            "content":query
        }
    )

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):

        with st.spinner("Analyzing business failure..."):

            answer = hybrid_rag(query)

            st.markdown(answer)

    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":answer
        }
    )
