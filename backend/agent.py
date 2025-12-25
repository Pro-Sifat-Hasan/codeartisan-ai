from typing import Annotated, TypedDict, List
from langchain_core.messages import BaseMessage  # type: ignore
from langchain_core.tools import tool # type: ignore
from langgraph.graph import StateGraph, START, END  # type: ignore
from langgraph.checkpoint.memory import MemorySaver # type: ignore
from langgraph.prebuilt import create_react_agent # type: ignore
from langchain_google_genai import ChatGoogleGenerativeAI # type: ignore
import os
from dotenv import load_dotenv

# import all tools
from backend.tools import edit_and_reapply
from backend.tools import fetch_url_content
from backend.tools import grep
from backend.tools import list_dir
from backend.tools import read_code
from backend.tools import read_file
from backend.tools import search_files
from backend.tools import search_web
from backend.tools import run_terminal 

# Load environment variables from .env file
load_dotenv()

# Set your API key
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

# Shared state across all agents
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "add_messages"]
    research: str
    architecture: str
    code: str
    review: str
    tests: str

llm = ChatGoogleGenerativeAI(model="gemini-3-pro-preview", temperature=0.3)

# 1. Research Agent - Gathers requirements and context
research_agent = create_react_agent(
    llm,
    tools=[search_web, read_file, grep, list_dir, fetch_url_content, search_files, read_code],  # Add web search, documentation fetch tools
    system_prompt="You research coding requirements, libraries, and best practices."
)

@tool
def research_task(description: str) -> str:
    """Research coding requirements and context."""
    result = research_agent.invoke({
        "messages": [{"role": "user", "content": f"Research: {description}"}]
    })
    return result["messages"][-1].content

# 2. Architect Agent - Designs system structure
architect_agent = create_react_agent(
    llm,
    tools=[search_files, list_dir, read_file, grep, fetch_url_content, read_code],  # Add diagram tools, architecture validators
    system_prompt="You design software architecture, file structure, and APIs."
)

@tool
def architect_task(requirements: str) -> str:
    """Design software architecture and file structure."""
    result = architect_agent.invoke({
        "messages": [{"role": "user", "content": f"Architecture for: {requirements}"}]
    })
    return result["messages"][-1].content

# 3. Code Writer Agent (Cursor-like) - Generates complete code
code_writer_agent = create_react_agent(
    llm,
    tools=[edit_and_reapply, read_file, read_code, list_dir, grep, search_files, run_terminal],  # Add file I/O, git tools for Cursor-like behavior
    system_prompt="""
    You are a Cursor-like code writing agent. Generate COMPLETE, production-ready code.
    Write full files with imports, error handling, tests, and documentation.
    Respond ONLY with formatted code blocks - no explanations.
    """
)

@tool
def write_code(spec: str) -> str:
    """Write complete, production-ready code from architecture spec."""
    result = code_writer_agent.invoke({
        "messages": [{"role": "user", "content": f"Write code for: {spec}"}]
    })
    return result["messages"][-1].content

# 4. Reviewer Agent - Code review and improvements
reviewer_agent = create_react_agent(
    llm,
    tools=[search_files, search_web, fetch_url_content, grep, list_dir, read_file, read_code],  # Add linting, security scanning tools
    system_prompt="You perform thorough code reviews focusing on bugs, security, and style."
)

@tool
def review_code(code: str) -> str:
    """Review code and suggest improvements."""
    result = reviewer_agent.invoke({
        "messages": [{"role": "user", "content": f"Review this code:\n{code}"}]
    })
    return result["messages"][-1].content

# 5. Tester Agent - Generates and runs tests
tester_agent = create_react_agent(
    llm,
    tools=[run_terminal, grep, list_dir, read_file, read_code],  # Add test runners, coverage tools
    system_prompt="You write comprehensive tests and validate code functionality."
)

@tool
def test_code(code: str) -> str:
    """Write tests and validate code."""
    result = tester_agent.invoke({
        "messages": [{"role": "user", "content": f"Test this code:\n{code}"}]
    })
    return result["messages"][-1].content

# Supervisor sees all agents as high-level tools
supervisor_tools = [research_task, architect_task, write_code, review_code, test_code]

supervisor = create_react_agent(
    llm,
    tools=supervisor_tools,
    system_prompt="""
    You coordinate a team of 5 coding agents to build complete applications:
    1. research_task: Gather requirements and context
    2. architect_task: Design system architecture  
    3. write_code: Generate COMPLETE production code (Cursor-like)
    4. review_code: Code review and improvements
    5. test_code: Write and run tests
    
    Workflow: Research → Architect → Code → Review → Test → Iterate if needed.
    Use multiple tools in sequence for complex tasks.
    """
)

# Compile the full multi-agent graph
checkpointer = MemorySaver()
graph = StateGraph(AgentState)
graph.add_node("supervisor", lambda state: supervisor.invoke(state))
graph.add_edge(START, "supervisor")
graph.add_conditional_edges(
    "supervisor",
    lambda state: END if not state["messages"][-1].tool_calls else "supervisor"
)
app = graph.compile(checkpointer=checkpointer)