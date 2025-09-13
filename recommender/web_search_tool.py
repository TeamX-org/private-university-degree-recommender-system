from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# DuckDuckGo search tool
duck_tool = DuckDuckGoSearchRun()

def web_search(query: str) -> str:
    """
    Web search using DuckDuckGo + Gemini summarization.
    Returns a concise answer.
    """
    raw_results = duck_tool.run(query)

    prompt = f"""
You are a helpful web search assistant. The user asked: "{query}".
Here are some web search results:

{raw_results}

Summarize and synthesize these results into a concise, clear, and useful answer.
"""
    response = gemini_model.generate_content(prompt)
    return response.text

# Wrap as a LangChain Tool
WebSearchTool = Tool(
    name="WebSearchTool",
    func=web_search,
    description="Use this tool to search the web and provide summarized answers."
)
