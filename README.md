Aerospace Diagnostic AI
This is an AI-powered assistant for aerospace technical documentation, enabling engineers and technicians to quickly find information and diagnose issues by asking natural language questions about their technical manuals.

The Problem
Aerospace systems are incredibly complex, with technical manuals often spanning thousands of pages. When an issue arises, sifting through dense documentation to find the precise procedure or specification can be a time-consuming and frustrating process. This operational friction leads to costly downtime, maintenance delays, and an increased risk of human error.

The Solution
This application provides a simple and intuitive interface to "chat" with complex technical documentation. By leveraging a Retrieval-Augmented Generation (RAG) pipeline, the system understands user questions, retrieves the most relevant information from the manuals, and generates a direct, accurate answer grounded in the provided text. This eliminates the need for manual searching and allows engineers to get the information they need instantly.

How It Works: The RAG Pipeline
The system operates in two main phases: an offline Ingestion Phase to process documents and an online Query Phase to answer questions.

1. Ingestion Phase: Processing and Indexing
This phase converts your raw technical manuals into a searchable knowledge base.

Document Upload: An engineer uploads technical manuals (PDF, DOC, TXT) through the Next.js frontend.

Text Extraction & Chunking: The FastAPI backend uses LangChain's document loaders to parse the files. The extracted text is then strategically divided into smaller, semantically meaningful chunks.

Embedding Generation: Each text chunk is passed through a Google Generative AI embedding model. This converts the text into a high-dimensional vector that numerically represents its semantic meaning.

Vector Storage: These embeddings, along with their corresponding text chunks and metadata, are stored in a Supabase project. Supabase uses PostgreSQL with the pgvector extension, which allows it to function as a powerful and scalable vector database.

2. Query Phase: Retrieval and Generation
This is the real-time process that occurs when a user asks a question.

User Query: A user asks a question in plain English, such as "What is the standard procedure for a hydraulic leak in section 7B?"

Query Embedding: The user's question is converted into a vector using the same Google embedding model.

Similarity Search: The system performs a vector similarity search in Supabase. It uses SQL-like queries (under the hood) to compare the question's vector against the millions of indexed chunks, instantly retrieving the most relevant snippets of text from the manuals.

Context Augmentation: The retrieved text chunks are assembled into a single block of context.

Answer Generation: This context is injected into a prompt for a powerful Google Generative AI model (like Gemini). The prompt effectively asks the model, "Using only the following information, answer the user's question."

Grounded Response: The model generates a direct, concise answer based only on the provided context, citing the source documents. This RAG approach ensures the answers are accurate and minimizes the risk of the AI "hallucinating" incorrect information.

Tech Stack
This project is a full-stack application built with the following technologies:

Frontend:

Next.js (React framework)

TypeScript

Tailwind CSS for styling

Backend:

FastAPI (Python web framework)

LangChain for document processing and RAG orchestration

Google Generative AI for language models and embeddings

Supabase for vector storage (PostgreSQL with pgvector)

Getting Started
Prerequisites
Node.js and npm

Python 3.8+

Supabase account and API credentials

Google Generative AI API key

1. Clone the repository
git clone [https://github.com/yogyam/AerospaceDiagnosticAssistant.git](https://github.com/yogyam/AerospaceDiagnosticAssistant.git)
cd AerospaceDiagnosticAssistant

2. Backend Setup
Navigate to the backend directory, create a virtual environment, and install the dependencies.

cd backend
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt

Create a .env file in the backend directory and add your credentials:

SUPABASE_URL="your_supabase_url_here"
SUPABASE_KEY="your_supabase_key_here"
GOOGLE_API_KEY="your_google_api_key_here"

3. Frontend Setup
Navigate back to the root directory and install the frontend dependencies:

cd ..
npm install

4. Running the Application
You will need two separate terminals to run both the backend and frontend servers.

Terminal 1: Start the Backend (FastAPI)

cd backend
source venv/bin/activate
uvicorn main:app --reload

The backend will be running at http://localhost:8000.

Terminal 2: Start the Frontend (Next.js)

cd ..
npm run dev

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.