import os
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.chains import RetrievalQA
import shutil
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize clients only if environment variables are set
supabase = None
embeddings = None
llm = None

if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL != "your_supabase_url_here":
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")

if GOOGLE_API_KEY and GOOGLE_API_KEY != "your_google_api_key_here":
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
        llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Google AI clients: {e}")

app = FastAPI()

# Enable CORS for all origins (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not supabase or not embeddings:
        return {"error": "Backend not properly configured. Please set SUPABASE_URL, SUPABASE_KEY, and GOOGLE_API_KEY in .env"}
    
    # Save file temporarily
    file_location = f"temp_{file.filename}"
    try:
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Load and split document
        loader = PyPDFLoader(file_location)
        pages = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(pages)

        # Embed and store in Supabase
        for doc in docs:
            content = doc.page_content
            try:
                embedding = embeddings.embed_query(content)
            except Exception as e:
                return {"error": f"Embedding failed: {str(e)}"}

            # Store in Supabase
            try:
                supabase.table("documents").insert({
                    "content": content,
                    "embedding": embedding,
                    "metadata": {"source": file.filename}
                }).execute()
            except Exception as e:
                return {"error": f"Supabase insert failed: {str(e)}"}
    finally:
        # Clean up temp file
        if os.path.exists(file_location):
            os.remove(file_location)

    return {"message": "Document processed and stored."}

@app.post("/ask")
async def ask_question(request: Request):
    if not supabase or not embeddings or not llm:
        return {"error": "Backend not properly configured. Please set SUPABASE_URL, SUPABASE_KEY, and GOOGLE_API_KEY in .env"}
    
    data = await request.json()
    question = data.get("question")
    if not question:
        return {"error": "No question provided."}

    try:
        vectorstore = SupabaseVectorStore(
            supabase_client=supabase,
            table_name="documents",
            embedding=embeddings
        )
        retriever = vectorstore.as_retriever()
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True
        )
        result = qa_chain({"query": question})
        return {"answer": result["result"], "sources": result["source_documents"]}
    except Exception as e:
        return {"error": f"Question answering failed: {str(e)}"}


