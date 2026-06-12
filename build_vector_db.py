import os
import json
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load .env
load_dotenv()

# Dataset folder
DATASET_FOLDER = "datasets"

documents = []

print("Loading JSON files...")

for file_name in os.listdir(DATASET_FOLDER):

    if file_name.endswith(".json"):

        file_path = os.path.join(DATASET_FOLDER, file_name)

        try:
            with open(file_path, "r", encoding="utf-8") as f:

                data = json.load(f)

                content = data.get("content", "")

                if content.strip():
                    documents.append(content)

        except Exception as e:
            print(f"Error reading {file_name}: {e}")

print(f"Loaded {len(documents)} documents")

# Chunking
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = []

for doc in documents:
    chunks.extend(splitter.split_text(doc))

print(f"Created {len(chunks)} chunks")

# HuggingFace Embeddings
print("Loading Embedding Model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Creating FAISS Vector Database...")

vector_db = FAISS.from_texts(
    texts=chunks,
    embedding=embeddings
)

print("Saving Vector Database...")

vector_db.save_local("vector_db")

print("✅ Vector DB Created Successfully!")