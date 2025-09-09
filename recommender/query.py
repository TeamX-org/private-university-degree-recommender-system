from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import cohere

# Load .env
load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Connect to Qdrant
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to Cohere
co = cohere.Client(COHERE_API_KEY)

def search_question(question, top_k=10, rerank_k=5):
    """
    Search the vector database, then rerank results with Cohere.
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

    # Step 3: Print reranked results
    print(f"\n🔎 Question: {question}\n")
    for idx, rerank in enumerate(rerank_response.results, 1):
        doc_index = rerank.index
        doc = results[doc_index]
        print(f"--- Reranked Result {idx} ---")
        print(f"Score: {rerank.relevance_score:.4f}")
        print(f"University: {doc.payload['university']}")
        print(f"Title/Section: {doc.payload['title']}")
        print(f"URL: {doc.payload['url']}")
        print(f"Chunk preview: {doc.payload['chunk'][:300]}...\n")

if __name__ == "__main__":
    question = input("Enter your question: ")
    search_question(question, top_k=10, rerank_k=5)
