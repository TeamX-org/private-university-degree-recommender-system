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

# Connect to Qdrant
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to Cohere
co = cohere.Client(COHERE_API_KEY)

# Connect to Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

def search_and_answer(question, top_k=10, rerank_k=5):
    """
    Search vector DB, rerank with Cohere, then generate an answer with Gemini.
    """
    # Step 1: Qdrant search
    query_vector = model.encode(question).tolist()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    ).points

    # Extract candidate chunks
    docs = [res.payload["chunk"] for res in results]

    # Step 2: Rerank with Cohere
    rerank_response = co.rerank(
        model="rerank-english-v3.0",
        query=question,
        documents=docs,
        top_n=rerank_k
    )

    # Collect top reranked docs
    top_chunks = []
    for rerank in rerank_response.results:
        doc = results[rerank.index]
        top_chunks.append(
            f"[{doc.payload['university']}] {doc.payload['title']} - {doc.payload['chunk']}"
        )

    # Step 3: Build context for Gemini
    context = "\n\n".join(top_chunks)
    prompt = f"""
You are an assistant helping students explore private universities in Sri Lanka.

Question: {question}

Here are some reference documents:
{context}

Based on these references, give a clear, well-structured, and creative answer.
If relevant, mention the universities by name.
"""

    # Step 4: Generate answer with Gemini
    response = gemini_model.generate_content(prompt)

    print("\n💡 Answer:\n")
    print(response.text)

if __name__ == "__main__":
    question = input("Enter your question: ")
    search_and_answer(question, top_k=10, rerank_k=5)
