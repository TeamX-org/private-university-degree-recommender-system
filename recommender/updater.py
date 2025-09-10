import requests
import uuid
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Build URLs dict from .env
urls = {}
for key, value in os.environ.items():
    if key.endswith("_URLS"):
        uni_name = key.replace("_URLS", "")
        urls[uni_name] = value.split(",")

# Connect to Qdrant with a long timeout
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=300  # 5 minutes timeout
)

# Create collection if it does not exist
if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
    )

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------- Helpers ----------------

def get_all_internal_links(base_url):
    try:
        resp = requests.get(base_url, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        links = set()
        for a_tag in soup.find_all("a", href=True):
            full_url = urljoin(base_url, a_tag['href'])
            if full_url.startswith(base_url):
                links.add(full_url)
        return links
    except Exception as e:
        print(f"⚠️ Error fetching {base_url}: {e}")
        return set()

def scrape_and_structure(url):
    try:
        res = requests.get(url, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        structured_chunks = []

        current_heading = "Main"
        content_accum = []

        for elem in soup.find_all(["h1", "h2", "h3", "p"]):
            if elem.name in ["h1", "h2", "h3"]:
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

        if content_accum:
            structured_chunks.append({
                "title": current_heading,
                "section": current_heading,
                "chunk": " ".join(content_accum)
            })

        return structured_chunks
    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")
        return []

def chunk_text(text, chunk_size=500):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

def upsert_points(points, batch_size=20, retry=3):
    """Upsert points in small batches with retries and delay"""
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        for attempt in range(retry):
            try:
                client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=batch
                )
                time.sleep(0.5)  # small delay between batches
                break
            except Exception as e:
                print(f"⚠️ Upsert failed (attempt {attempt+1}): {e}")
                time.sleep(5)
        else:
            print("❌ Failed to upsert batch after retries.")

def ingest_url(url, uni_name):
    structured_chunks = scrape_and_structure(url)
    if not structured_chunks:
        print(f"⚠️ No text found at {url}")
        return

    points = []
    for section in structured_chunks:
        for chunk in chunk_text(section["chunk"]):
            embedding = model.encode(chunk).tolist()
            points.append(
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
            )
    upsert_points(points)

# ---------------- Main ----------------

if __name__ == "__main__":
    for uni, base_urls in urls.items():
        all_links = set()
        for base_url in base_urls:
            print(f"🌐 Crawling {uni} ({base_url})...")
            links = get_all_internal_links(base_url)
            print(f"➡️ Found {len(links)} pages for {uni}")
            all_links.update(links)

        for idx, link in enumerate(all_links, 1):
            print(f"➡️ [{idx}/{len(all_links)}] Ingesting: {link}")
            ingest_url(link, uni)

    print("✅ Data ingestion complete!")
