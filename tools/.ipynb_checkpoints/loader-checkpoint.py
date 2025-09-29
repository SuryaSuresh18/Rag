# tools/loader.py
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter

def load_and_chunk_pdf(pdf_path):
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(documents)
