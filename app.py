import os
from dotenv import load_dotenv
import streamlit as st

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

from langchain_community.vectorstores import FAISS

load_dotenv()

# Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

# Embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001"
)

# Load Vector DB
db = FAISS.load_local(
    "vector_db",
    embeddings,
    allow_dangerous_deserialization=True
)

# UI
st.set_page_config(
    page_title="Failure Intelligence RAG",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Failure Intelligence RAG")
st.write(
    "Analyze Startup, Google, and Amazon Product Failures"
)

query = st.text_input(
    "Ask a question..."
)

if query:

    with st.spinner("Searching knowledge base..."):

        docs = db.similarity_search(
            query,
            k=5
        )

        context = "\n\n".join(
            [doc.page_content for doc in docs]
        )

        prompt = f"""
You are an expert startup and product failure analyst.

Use ONLY the provided context.

Context:
{context}

Question:
{query}

Provide:
1. Direct Answer
2. Key Failure Reasons
3. Lessons Learned
4. Recommendations

If information is not present in the context, say so.
"""

        response = llm.invoke(prompt)

        st.subheader("Answer")
        st.write(response.content)

        with st.expander("Retrieved Context"):

            for i, doc in enumerate(docs, start=1):

                st.markdown(
                    f"### Document {i}"
                )

                st.write(
                    doc.page_content[:1500]
                )