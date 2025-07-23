# Aerospace Diagnostic AI

This is an AI-powered assistant for aerospace technical documentation, enabling engineers and technicians to quickly find information and diagnose issues by asking natural language questions about their technical manuals.

## The Problem

Aerospace systems are incredibly complex, with technical manuals often spanning thousands of pages. When an issue arises, finding the precise piece of information needed to diagnose or fix it can be a time-consuming and frustrating process. This can lead to costly downtime and delays.

## The Solution

This application provides a simple and intuitive interface for interacting with complex technical documentation. Users can upload their manuals in various formats (PDF, DOC, TXT), and the system will process and index them. Once indexed, users can ask questions in plain English, and the AI assistant will provide a direct answer, complete with citations from the original documents.

## Tech Stack

This project is a full-stack application built with the following technologies:

*   **Frontend:**
    *   [Next.js](https://nextjs.org/) (React framework)
    *   [TypeScript](https://www.typescriptlang.org/)
    *   [Tailwind CSS](https://tailwindcss.com/) for styling
*   **Backend:**
    *   [FastAPI](https://fastapi.tiangolo.com/) (Python web framework)
    *   [LangChain](https://www.langchain.com/) for document processing and RAG
    *   [Google Generative AI](https://ai.google/discover/generativeai/) for language models and embeddings
    *   [Supabase](https://supabase.com/) for vector storage

## Getting Started

### Prerequisites

- Node.js and npm
- Python 3.8+
- Supabase account and API credentials
- Google Generative AI API key

### 1. Clone the repository

```bash
git clone https://github.com/yogyam/AerospaceDiagnosticAssistant.git
cd AerospaceDiagnosticAssistant
```

### 2. Backend Setup

Navigate to the backend directory, create a virtual environment, and install the dependencies.

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory and add your credentials:

```
SUPABASE_URL="your_supabase_url_here"
SUPABASE_KEY="your_supabase_key_here"
GOOGLE_API_KEY="your_google_api_key_here"
```

### 3. Frontend Setup

Navigate back to the root directory and install the frontend dependencies:

```bash
cd ..
npm install
```

### 4. Running the Application

You will need two separate terminals to run both the backend and frontend servers.

**Terminal 1: Start the Backend (FastAPI)**

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

The backend will be running at `http://localhost:8000`.

**Terminal 2: Start the Frontend (Next.js)**

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.
