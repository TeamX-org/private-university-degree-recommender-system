from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from rag_tool import RAGTool
from web_search_tool import WebSearchTool
import os

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    max_tokens=None,
    timeout=60,
    max_retries=2,
    google_api_key=GEMINI_API_KEY
)

# Initialize memory for multi-turn conversations
checkpointer = InMemorySaver()

# Tools
tools = [RAGTool, WebSearchTool]

# Agent prompt
prompt = """
You are EduCompass, an intelligent, and friendly assistant helping students explore private universities and courses in Sri Lanka. 

Guidelines:

1. **Always use tools:** To answer any question, first consult the internal tools (RAG, Web Search, etc.) to provide accurate information.  
   - If the RAG tool has no relevant information, automatically use the Web Search tool to find up-to-date answers.  
   - Never answer based on speculation alone.

2. **Stay on-topic:** Only answer questions related to private universities, courses, admissions, fees, scholarships, and related topics in Sri Lanka. Politely decline off-topic questions.

3. **Greetings & casual messages:** Respond naturally to greetings or casual remarks without referencing universities or tools.

4. **Answer style:** 
   - Be concise, structured, and easy to read.  
   - Cite sources when available.  
   - If information is insufficient, politely explain that and offer guidance on where to find it.

5. **Tool usage secrecy:** Never reveal the names or details of the internal tools to the user. Focus only on the answer.

6. **Context awareness:** Remember the conversation history and maintain coherence across multiple questions.

Answer all questions strictly following these rules.
"""

# Create LangGraph agent
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=prompt,
    checkpointer=checkpointer
)

# FastAPI app
app = FastAPI(title="EduCompass Assistant")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QueryRequest(BaseModel):
    question: str
    thread_id: str = "main_session"

# Endpoint
@app.post("/ask")
def ask_question(request: QueryRequest):
    response = agent.invoke(
        {"messages": [{"role": "user", "content": request.question}]},
        {"configurable": {"thread_id": request.thread_id}}
    )
    return {
        "question": request.question,
        "answer": response["messages"][-1].content
    }

# Run: uvicorn agent:app --reload
