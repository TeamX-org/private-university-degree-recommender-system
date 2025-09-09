from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Connect to Qdrant
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_question(question, top_k=5):
    """
    Search the vector database for the question across all universities.
    """
    query_vector = model.encode(question).tolist()

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )

    for idx, res in enumerate(results, 1):
        print(f"--- Result {idx} ---")
        print(f"University: {res.payload['university']}")
        print(f"Title/Section: {res.payload['title']}")
        print(f"URL: {res.payload['url']}")
        print(f"Chunk preview: {res.payload['chunk'][:300]}...\n")

if __name__ == "__main__":
    question = input("Enter your question: ")
    search_question(question, top_k=5)
