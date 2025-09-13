from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import cohere
import google.generativeai as genai

# Load .env
load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize clients
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
model = SentenceTransformer("all-MiniLM-L6-v2")
co = cohere.Client(COHERE_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# FastAPI app
app = FastAPI(title="Web Assistant")

# Add this for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    top_k: int = 10
    rerank_k: int = 5

@app.post("/ask")
def ask_question(request: QueryRequest):
    """
    Takes a question, searches Qdrant, reranks with Cohere, 
    and generates an answer with Gemini.
    """
    # Step 1: Qdrant search
    query_vector = model.encode(request.question).tolist()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=request.top_k
    ).points

    if not results:
        return {"answer": "No relevant information found in the database."}

    # Step 2: Rerank with Cohere
    docs = [res.payload["chunk"] for res in results]
    rerank_response = co.rerank(
        model="rerank-english-v3.0",
        query=request.question,
        documents=docs,
        top_n=request.rerank_k
    )

    # Step 3: Collect reranked docs
    top_chunks = []
    for rerank in rerank_response.results:
        doc = results[rerank.index]
        top_chunks.append(
            f"[{doc.payload['university']}] {doc.payload['title']} - {doc.payload['chunk']}"
        )

    context = "\n\n".join(top_chunks)
    prompt = f"""
You are an assistant that helps students explore private universities and courses in Sri Lanka.

If the user's question is clearly a greeting (like "hi", "hello", "thanks", etc.), 
reply naturally and friendly without mentioning universities or references.

If the user's question is about private universities or courses in Sri Lanka,
use the reference documents below to give a clear, concise, and helpful answer.

If the answer is not in the references, politely say you don’t have enough information.

Question: {request.question}

Reference Documents:
{context}
"""

    # Step 4: Response
    response = gemini_model.generate_content(prompt)

    return {
        "question": request.question,
        "answer": response.text,
        "sources": top_chunks
    }
