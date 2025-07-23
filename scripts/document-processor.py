"""
Document Processing Script for Aerospace RAG System
This script demonstrates how to process aerospace documents and store them in Supabase
"""

import os
import json
from typing import List, Dict
import openai
from supabase import create_client, Client
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def initialize_clients():
    """Initialize Supabase and OpenAI clients"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    openai.api_key = OPENAI_API_KEY
    embeddings = OpenAIEmbeddings()
    return supabase, embeddings

def load_and_split_document(file_path: str) -> List[Dict]:
    """Load a PDF document and split it into chunks"""
    
    # Load the document
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(pages)
    
    # Format chunks with metadata
    formatted_chunks = []
    for i, chunk in enumerate(chunks):
        formatted_chunks.append({
            'content': chunk.page_content,
            'metadata': {
                'document': os.path.basename(file_path),
                'page': chunk.metadata.get('page', 0),
                'chunk_index': i,
                'source': file_path
            }
        })
    
    return formatted_chunks

def generate_embeddings(chunks: List[Dict], embeddings_client) -> List[Dict]:
    """Generate embeddings for document chunks"""
    
    for chunk in chunks:
        # Generate embedding for the content
        embedding = embeddings_client.embed_query(chunk['content'])
        chunk['embedding'] = embedding
    
    return chunks

def store_in_supabase(supabase: Client, chunks: List[Dict]):
    """Store document chunks and embeddings in Supabase"""
    
    for chunk in chunks:
        try:
            result = supabase.table('documents').insert({
                'content': chunk['content'],
                'embedding': chunk['embedding'],
                'metadata': chunk['metadata']
            }).execute()
            
            print(f"Stored chunk from {chunk['metadata']['document']} page {chunk['metadata']['page']}")
            
        except Exception as e:
            print(f"Error storing chunk: {e}")

def process_aerospace_document(file_path: str):
    """Main function to process an aerospace document"""
    
    print(f"Processing document: {file_path}")
    
    # Initialize clients
    supabase, embeddings = initialize_clients()
    
    # Load and split document
    print("Loading and splitting document...")
    chunks = load_and_split_document(file_path)
    print(f"Created {len(chunks)} chunks")
    
    # Generate embeddings
    print("Generating embeddings...")
    chunks_with_embeddings = generate_embeddings(chunks, embeddings)
    
    # Store in database
    print("Storing in Supabase...")
    store_in_supabase(supabase, chunks_with_embeddings)
    
    print(f"Successfully processed {file_path}")

def batch_process_documents(directory_path: str):
    """Process all PDF documents in a directory"""
    
    pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]
    
    for pdf_file in pdf_files:
        file_path = os.path.join(directory_path, pdf_file)
        try:
            process_aerospace_document(file_path)
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")

if __name__ == "__main__":
    # Example usage
    # process_aerospace_document("path/to/your/aerospace_manual.pdf")
    # batch_process_documents("path/to/your/documents/directory")
    
    print("Document processor ready!")
    print("Usage:")
    print("1. Set environment variables: SUPABASE_URL, SUPABASE_ANON_KEY, OPENAI_API_KEY")
    print("2. Call process_aerospace_document(file_path) for single files")
    print("3. Call batch_process_documents(directory_path) for batch processing")
