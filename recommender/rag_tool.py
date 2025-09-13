from langchain.tools import Tool
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import cohere
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize clients
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
co = cohere.Client(COHERE_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")


def rag_search(question: str, top_k: int = 10, rerank_k: int = 5) -> str:
    """RAG tool: Search Qdrant database, rerank with Cohere reranker, generate answer with Gemini."""
    # Step 1: Encode query & search Qdrant
    query_vector = sbert_model.encode(question).tolist()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    ).points

    if not results:
        return "No relevant information found in the database."

    # Step 2: Rerank with Cohere
    docs = [res.payload["chunk"] for res in results]
    rerank_response = co.rerank(
        model="rerank-english-v3.0",
        query=question,
        documents=docs,
        top_n=rerank_k
    )

    # Step 3: Collect top chunks
    top_chunks = []
    for rerank in rerank_response.results:
        doc = results[rerank.index]
        top_chunks.append(
            f"[{doc.payload['university']}] {doc.payload['title']} - {doc.payload['chunk']}"
        )

    context = "\n\n".join(top_chunks)
    prompt = f"""
You are a retrieval-augmented generation (RAG) assistant helping students explore private universities and courses in Sri Lanka.

Question: {question}

Here are some reference documents:
{context}

Based on these references, give a clear, well-structured, and creative answer.
If the answer is not in the references, politely say you don’t have enough information.
"""

    # Step 4: Generate answer
    response = gemini_model.generate_content(prompt)
    return response.text


# Wrap as a LangChain tool
RAGTool = Tool(
    name="RAGTool",
    func=rag_search,
    description="Use this tool to answer questions about private universities in Sri Lanka using a vector database and LLM."
)
