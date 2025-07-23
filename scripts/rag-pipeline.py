"""
RAG Pipeline Implementation for Aerospace Anomaly Detection
This script demonstrates the complete RAG pipeline using LangChain
"""

import os
from typing import List, Dict, Any
from langchain.vectorstores import SupabaseVectorStore
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from supabase import create_client, Client

class AerospaceRAGPipeline:
    def __init__(self):
        """Initialize the RAG pipeline with Supabase and OpenAI"""
        
        # Environment variables
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize clients
        self.supabase_client = create_client(self.supabase_url, self.supabase_key)
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.llm = OpenAI(openai_api_key=self.openai_api_key, temperature=0.3)
        
        # Initialize vector store
        self.vector_store = SupabaseVectorStore(
            client=self.supabase_client,
            embedding=self.embeddings,
            table_name="documents",
            query_name="search_documents"
        )
        
        # Create the RAG chain
        self.setup_rag_chain()
    
    def setup_rag_chain(self):
        """Set up the RAG chain with custom prompt template"""
        
        # Custom prompt template for aerospace diagnostics
        prompt_template = """You are an expert aerospace diagnostic AI assistant. Use the following retrieved documents to answer questions about aerospace systems, anomaly detection, and technical troubleshooting.

INSTRUCTIONS:
- Base your answer on the provided context documents
- If the context doesn't contain sufficient information, clearly state this
- Provide specific technical details, parameters, and procedures when available
- Include relevant safety considerations and warnings
- Be precise and professional in your response
- Reference specific documents or sections when possible

Context Documents:
{context}

Question: {question}

Expert Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create the retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 5}  # Retrieve top 5 most relevant chunks
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """Ask a question and get an answer with sources"""
        
        try:
            # Run the RAG chain
            result = self.qa_chain({"query": question})
            
            # Format the response
            response = {
                "answer": result["result"],
                "sources": [],
                "retrieved_chunks": len(result["source_documents"])
            }
            
            # Extract source information
            for doc in result["source_documents"]:
                source_info = {
                    "content": doc.page_content[:200] + "...",  # First 200 chars
                    "metadata": doc.metadata
                }
                response["sources"].append(source_info)
            
            return response
            
        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error: {str(e)}",
                "sources": [],
                "retrieved_chunks": 0
            }
    
    def search_similar_documents(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar documents without generating an answer"""
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

def main():
    """Example usage of the RAG pipeline"""
    
    # Initialize the pipeline
    rag = AerospaceRAGPipeline()
    
    # Example questions
    test_questions = [
        "What are the normal operating pressure ranges for hydraulic systems?",
        "How do engine anomaly detection systems work?",
        "What should I do if flight control actuators show position discrepancies?",
        "What are the signs of avionics power supply issues?",
        "How long should landing gear retraction take?"
    ]
    
    print("Aerospace RAG Pipeline - Interactive Demo")
    print("=" * 50)
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        print("-" * 40)
        
        response = rag.ask_question(question)
        
        print(f"Answer: {response['answer']}")
        print(f"Sources: {response['retrieved_chunks']} documents retrieved")
        
        if response['sources']:
            print("\nSource Documents:")
            for i, source in enumerate(response['sources'][:2], 1):
                metadata = source['metadata']
                print(f"  {i}. {metadata.get('document', 'Unknown')} (Page {metadata.get('page', 'N/A')})")
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
