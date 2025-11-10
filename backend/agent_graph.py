from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from notion_utils import create_notion_page
import os, json, re
from dotenv import load_dotenv

# -------------------- Load environment variables --------------------
load_dotenv()

# -------------------- Initialize Gemini (AI Studio API key) --------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  # or "gemini-2.0-flash" if available
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.4,
)

# -------------------- Define LangGraph State --------------------
class AgentState(TypedDict):
    user_prompt: str
    title: str
    note_content: str
    result: str


graph = StateGraph(AgentState)


# -------------------- Node 1: Interpret Prompt --------------------
def interpret_prompt(state: AgentState):
    """
    This node takes the user's natural language input and generates
    a structured, markdown-formatted note that can be converted into
    Notion blocks by the formatter.
    """

    user_prompt = state["user_prompt"]

    system_prompt = f"""
    You are a helpful AI assistant that creates structured Notion notes
    based on user instructions.
    
    Your job is to analyze the input and generate clean, organized markdown
    that represents the intended note.
    
    Formatting Rules:
    - Use Markdown syntax.
    - Use `#`, `##`, `###` for headings.
    - Use `- [ ]` or `- [x]` for checkboxes or tasks.
    - Use `-` for bullet lists and `1.` for numbered lists.
    - Use `> ` for quotes.
    - Use triple backticks (```) for code blocks.
    - Use markdown tables for tabular data (| Col1 | Col2 |).
    - Keep it well formatted and ready to convert to Notion blocks.
    - Include a clear title as a first-level heading (# Title).
    
    Example output:
    
    Now create a properly formatted markdown note for the following instruction:
    {user_prompt}
    """

    # Get LLM response
    response = llm.invoke(system_prompt)
    text = response.content.strip()

    # Default values
    title = "Untitled"
    content = text

    # Try parsing JSON output if the LLM accidentally returns JSON
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            title = data.get("title", "Untitled").strip()
            content = data.get("content", text).strip()
        except Exception:
            pass
    else:
        # Try extracting title from first markdown heading
        heading_match = re.search(r"^#\s*(.+)", text, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1).strip()

    return {"title": title, "note_content": content}


# -------------------- Node 2: Create Note in Notion --------------------
def create_note(state: AgentState):
    """
    Cleans markdown and creates Notion page with parsed blocks.
    """
    title = state["title"]
    content = state["note_content"]

    # 🧹 Clean Gemini output — remove Markdown code fences
    content = re.sub(r"^```[a-zA-Z0-9]*\n", "", content.strip())  # remove opening ```
    content = re.sub(r"```$", "", content.strip())  # remove closing ```
    content = content.strip()

    try:
        page = create_notion_page(title, content)
        return {"result": f"✅ Note created successfully: {page['url']}"}
    except Exception as e:
        return {"result": f"❌ Failed to create note: {str(e)}"}



# -------------------- Build LangGraph Workflow --------------------
graph.add_node("interpret", interpret_prompt)
graph.add_node("create", create_note)

graph.add_edge(START, "interpret")
graph.add_edge("interpret", "create")
graph.add_edge("create", END)

# Compile into an executable app
agent_app = graph.compile()
