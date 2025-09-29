# agents/rag_agent.py

import os
from langchain.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from tools.loader import load_and_chunk_pdf
from config import PDF_PATH, MODEL_NAME

# Define where FAISS index will be stored
FAISS_INDEX_PATH = os.path.join("data", "faiss_index")

# ✅ Singleton RAG chain (to avoid rebuilding)
_rag_chain = None

def build_rag_agent():
    """
    Builds or loads the RAG agent using FAISS vector store and Ollama.
    Ensures embeddings and indexing are done only once.
    """
    global _rag_chain
    if _rag_chain is not None:
        print("✅ RAG already initialized – using cached instance")
        return _rag_chain  # ✅ Return cached chain

    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)

    print("🔄 Loading embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    faiss_index_file = os.path.join(FAISS_INDEX_PATH, "index.faiss")
    if os.path.exists(faiss_index_file):
        print("✅ Loading existing FAISS vector store from disk...")
        vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        print("🔄 Loading and chunking PDF...")
        chunks = load_and_chunk_pdf(PDF_PATH)
        print(f"✅ Loaded {len(chunks)} chunks")

        print("🔄 Creating and saving FAISS vector store...")
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(FAISS_INDEX_PATH)
        print("✅ FAISS vector store saved at", FAISS_INDEX_PATH)

    llm = Ollama(model=MODEL_NAME)
    print("✅ Ollama LLM loaded")

    retriever = vectorstore.as_retriever()
    _rag_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    return _rag_chain

def answer_with_rag(query):
    rag_chain = build_rag_agent()
    import time
    start = time.time()
    result = rag_chain.invoke(query)
    print(f"⏱️ RAG invoke took {time.time() - start:.2f} seconds")
    return result

