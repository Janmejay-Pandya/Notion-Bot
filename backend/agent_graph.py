from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from notion_utils import create_notion_page
import os
from dotenv import load_dotenv

load_dotenv()
# Initialize Gemini via LangChain wrapper
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.4,
)
# Define state schema
class AgentState(TypedDict):
    user_prompt: str
    title: str
    note_content: str
    result: str

graph = StateGraph(AgentState)

# Node 1: interpret user's prompt using Gemini
def interpret_prompt(state: AgentState):
    user_prompt = state["user_prompt"]
    system_prompt = (
        "You are a helpful AI note-creator. "
        "Extract a short descriptive title and detailed note content "
        "from the user's instruction. Respond strictly in JSON format: "
        '{"title": "...", "content": "..."}.\n\n'
        f"Instruction: {user_prompt}"
    )

    response = llm.invoke(system_prompt)
    text = response.content.strip()

    import json, re
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            title = data.get("title", "Untitled").strip()
            content = data.get("content", "").strip()
        except Exception:
            title, content = "Untitled", text
    else:
        title, content = "Untitled", text

    return {"title": title, "note_content": content}

# Node 2: create note in Notion
def create_note(state: AgentState):
    page = create_notion_page(state["title"], state["note_content"])
    return {"result": f"✅ Note created: {page['url']}"}

# Build graph
graph.add_node("interpret", interpret_prompt)
graph.add_node("create", create_note)

graph.add_edge(START, "interpret")
graph.add_edge("interpret", "create")
graph.add_edge("create", END)

agent_app = graph.compile()
