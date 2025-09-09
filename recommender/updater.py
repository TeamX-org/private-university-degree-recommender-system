import requests
import uuid
from bs4 import BeautifulSoup
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Dynamically build urls dict from environment
urls = {}
for key, value in os.environ.items():
    if key.endswith("_URLS"):
        uni_name = key.replace("_URLS", "")
        urls[uni_name] = value.split(",")

# Connect to Qdrant
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Create collection
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Helper: extract structured content
def scrape_and_structure(url):
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    structured_chunks = []

    # Track current heading
    current_heading = "Main"
    content_accum = []

    # Iterate over elements
    for elem in soup.find_all(["h1", "h2", "h3", "p"]):
        if elem.name in ["h1", "h2", "h3"]:
            # Save previous chunk
            if content_accum:
                structured_chunks.append({
                    "title": current_heading,
                    "section": current_heading,
                    "chunk": " ".join(content_accum)
                })
                content_accum = []
            current_heading = elem.get_text().strip()
        elif elem.name == "p":
            text = elem.get_text().strip()
            if text:
                content_accum.append(text)

    # Save any remaining content
    if content_accum:
        structured_chunks.append({
            "title": current_heading,
            "section": current_heading,
            "chunk": " ".join(content_accum)
        })

    return structured_chunks

# Helper: split large chunks
def chunk_text(text, chunk_size=500):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

def ingest_url(url, uni_name):
    structured_chunks = scrape_and_structure(url)
    if not structured_chunks:
        print(f"⚠️ No text found at {url}")
        return

    for section in structured_chunks:
        for chunk in chunk_text(section["chunk"]):
            embedding = model.encode(chunk).tolist()
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            "university": uni_name,
                            "url": url,
                            "title": section["title"],
                            "section": section["section"],
                            "chunk": chunk
                        }
                    )
                ],
            )

if __name__ == "__main__":
    for uni, links in urls.items():
        print(f"Ingesting {uni}...")
        for link in links:
            ingest_url(link, uni)

    print("✅ Data ingested into Qdrant!")
