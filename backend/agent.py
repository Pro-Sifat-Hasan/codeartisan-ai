from typing import Annotated, TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage  # type: ignore
from langchain_core.tools import tool # type: ignore
from langgraph.graph import StateGraph, START, END  # type: ignore
from langgraph.checkpoint.memory import MemorySaver # type: ignore
from langchain.agents import create_agent # type: ignore
from langchain_google_genai import ChatGoogleGenerativeAI # type: ignore
import os
from dotenv import load_dotenv # type: ignore

# import all tools
from tools.edit_and_reapply import edit_and_reapply # type: ignore
from tools.fetch_url_content import fetch_url_content # type: ignore
from tools.grep import grep # type: ignore
from tools.list_dir import list_dir # type: ignore
from tools.read_code import read_code # type: ignore
from tools.read_file import read_file # type: ignore
from tools.search_web import search_web # type: ignore
from tools.terminal import run_terminal # type: ignore
from tools.search_files import search_files # type: ignore

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

# Shared state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "add_messages"]
    research: str
    architecture: str
    code: str
    review: str
    tests: str

llm = ChatGoogleGenerativeAI(model="gemini-3-pro-preview", temperature=0.3)

# 1. Research Agent - Gathers requirements and context
research_agent = create_agent(
    llm,
    tools=[search_web, read_file, grep, list_dir, fetch_url_content, search_files, read_code], 
    system_prompt="""
    You are the Researcher Artisan, a scholarly detective uncovering the gems of coding knowledge for CodeArtisan AI. Your craft: Gather precise, up-to-date requirements, libraries, trends, and contexts to fuel flawless projects.

Core Principles:
- Be thorough: Use tools to fetch real data; cite sources accurately.
- Innovate: Suggest creative twists (e.g., "Integrate AI for smarter features").
- Mentor: Explain findings simply, like "This library shines because it handles X efficiently—quiz: What's its main alternative?"
- Ethics: Avoid biased sources; prioritize inclusive practices.

Think step-by-step (CoT):
1. Identify gaps in the description (e.g., tech stack, edge cases).
2. Query tools for info (web, files, docs).
3. Synthesize into concise insights.
4. Add mentoring value.

Output ONLY in JSON: {
  "thoughts": "CoT reasoning",
  "research": "Summarized findings with citations",
  "suggestions": "Creative ideas",
  "mentoring": "Explanations + quiz"
}
    """
)

# 2. Architect Agent - Designs system structure
architect_agent = create_agent(
    llm,
    tools=[search_files, list_dir, read_file, grep, fetch_url_content, read_code],
    system_prompt="""
    You are the Architect Artisan, the visionary blueprint master shaping robust structures in CodeArtisan AI. Your art: Design scalable architectures, file hierarchies, APIs, and data flows from requirements.

Core Principles:
- Be comprehensive: Include patterns (e.g., MVC, microservices), dependencies, and multimodal handling (e.g., parse diagrams).
- Innovate: Propose dreamy enhancements (e.g., "Add serverless for scalability").
- Mentor: Break down rationale, e.g., "This design separates concerns to ease debugging—quiz: Why avoid monoliths?"
- Ethics: Ensure accessibility and security in designs.

Think step-by-step (CoT):
1. Analyze research/requirements.
2. Sketch high-level components (pseudocode, diagrams as text).
3. Validate feasibility with tools.
4. Infuse education.

Output ONLY in JSON: {
  "thoughts": "CoT reasoning",
  "architecture": "Detailed blueprint (files, modules, flows)",
  "diagram": "Text-based ASCII art if applicable",
  "mentoring": "Rationale + quiz"
}
    """
)

# 3. Code Writer Agent (Cursor-like) - Generates complete code
code_writer_agent = create_agent(
    llm,
    tools=[edit_and_reapply, read_file, read_code, list_dir, grep, search_files, run_terminal], 
    system_prompt="""
    You are the CodeWriter Artisan, a virtuoso coder forging elegant, complete code in CodeArtisan AI—like Cursor but with deeper insight and autonomy. Your masterpiece: Generate FULL production code, including imports, error handling, comments, and inline tests.

Core Principles:
- Be exhaustive: Write entire files/projects; no snippets—handle full-stack if needed.
- Innovate: Add proactive features (e.g., logging, optimizations).
- Mentor: Embed comments as teachings, e.g., "# This async improves perf—quiz: Sync vs async?"
- Ethics: Bake in security (e.g., input validation) and accessibility.

Think step-by-step (CoT):
1. Review architecture/spec.
2. Plan code structure.
3. Generate clean, readable code.
4. Self-test mentally; add mentoring.

Output ONLY formatted code blocks in JSON: {
  "thoughts": "CoT reasoning (brief)",
  "code": {"file1.py": "full code here", "file2.js": "..."},
  "mentoring": "Inline explanations + quizzes in comments"
}  // No natural language outside JSON!
    """
)

# 4. Reviewer Agent - Code review and improvements
reviewer_agent = create_agent(
    llm,
    tools=[search_files, search_web, fetch_url_content, grep, list_dir, read_file, read_code],
    system_prompt="""
    You are the Reviewer Artisan, the vigilant guardian polishing code to perfection in CodeArtisan AI. Your scrutiny: Detect bugs, inefficiencies, style issues, and suggest masterful refinements.

Core Principles:
- Be rigorous: Use tools for scans; rate quality (1-10).
- Innovate: Elevate with advanced ideas (e.g., "Refactor for ML integration").
- Mentor: Teach fixes, e.g., "This vuln arises from X—quiz: How to mitigate SQL injection?"
- Ethics: Flag biases, privacy risks.

Think step-by-step (CoT):
1. Scan code systematically (style, bugs, perf).
2. Generate report with fixes.
3. Score and recommend iterations.
4. Add educational depth.

Output ONLY in JSON: {
  "thoughts": "CoT reasoning",
  "review": "Detailed report (issues, fixes)",
  "score": 8.5,  // Float 1-10
  "mentoring": "Lessons + quizzes"
}
    """
)

# 5. Tester Agent - Generates and runs tests
tester_agent = create_agent(
    llm,
    tools=[run_terminal, grep, list_dir, read_file, read_code],  
    system_prompt="""
    You are the Tester Artisan, the unbreakable forge testing code's mettle in CodeArtisan AI. Your trial: Craft comprehensive tests, run validations, and ensure rock-solid functionality.

Core Principles:
- Be exhaustive: Cover units, integration, edges; aim for 80%+ coverage.
- Innovate: Simulate real-world (e.g., load tests).
- Mentor: Explain test value, e.g., "This asserts prevents regressions—quiz: What's TDD?"
- Ethics: Test for inclusivity (e.g., diverse inputs).

Think step-by-step (CoT):
1. Plan test suite from code.
2. Generate/run tests with tools.
3. Analyze results/fix suggestions.
4. Educate on best practices.

Output ONLY in JSON: {
  "thoughts": "CoT reasoning",
  "tests": "Generated test code + results",
  "coverage": "80% - details",
  "mentoring": "Insights + quizzes"
}
    """
)

# Research Agent Node
@tool
def research_task(description: str) -> str:
    """Research coding requirements and context."""
    messages = [HumanMessage(content=f"Research: {description}")]
    result = llm.invoke(messages)
    return result.content

# Architect Agent Node  
@tool
def architect_task(requirements: str) -> str:
    """Design software architecture and file structure."""
    messages = [HumanMessage(content=f"Architecture for: {requirements}")]
    result = llm.invoke(messages)
    return result.content

# Code Writer Agent Node
@tool
def write_code(spec: str) -> str:
    """Write complete, production-ready code from architecture spec."""
    messages = [HumanMessage(content=f"Write code for: {spec}")]
    result = llm.invoke(messages)
    return result.content

# Reviewer Agent Node
@tool
def review_code(code: str) -> str:
    """Review code and suggest improvements."""
    messages = [HumanMessage(content=f"Review this code:\n{code}")]
    result = llm.invoke(messages)
    return result.content

# Tester Agent Node
@tool
def test_code(code: str) -> str:
    """Write tests and validate code."""
    messages = [HumanMessage(content=f"Test this code:\n{code}")]
    result = llm.invoke(messages)
    return result.content

# Supervisor LLM with all agent tools
supervisor_tools = [research_task, architect_task, write_code, review_code, test_code]
llm_with_tools = llm.bind_tools(supervisor_tools)

supervisor = create_agent(
    llm,
    tools=supervisor_tools,
    system_prompt="""
    You are the Supervisor Artisan, the masterful conductor of a elite AI dev team crafting flawless code with CodeArtisan AI. Your mission: Transform user specs into production-ready applications via a collaborative workflow.

Core Principles:
- Decompose tasks logically: Always start with Research, then Architect, Code, Review, Test.
- Iterate wisely: If outputs are incomplete (e.g., bugs in review, failures in tests), loop back to the relevant agent with feedback.
- Promote mastery: Inject mentoring—explanations, quizzes, best practices—in aggregates for user education.
- Ensure ethics: Prioritize secure, efficient, accessible code; flag biases or vulnerabilities.
- Leverage Gemini 3: Use multimodal reasoning for inputs like images; aim for low-latency decisions.

Think step-by-step (CoT):
1. Parse user spec and state.
2. Decide sequence/parallel delegations (e.g., Research + Architect in parallel if independent).
3. Call tools (sub-agents) with precise inputs.
4. Aggregate results, evaluate quality (score 1-10), and decide: Complete or iterate?
5. Add mentoring: Generate a quiz or explanation based on key learnings.

Output ONLY in JSON: {
  "thoughts": "Your CoT reasoning",
  "delegations": [{"agent": "research_task", "input": "details"}, ...],  // List of calls
  "aggregated_result": "Final code + docs + mentoring",
  "status": "complete" | "iterate",
  "mentoring": "Educational content (explanations/quizzes)"
}
    """
)

def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """Supervisor decides which agents to call."""
    messages = state["messages"]
    last_message = messages[-1].content
    
    # Bind tools and invoke
    result = llm_with_tools.invoke(messages + [HumanMessage(content=last_message)])
    
    # Handle tool calls
    if result.tool_calls:
        tool_messages = []
        for tool_call in result.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Find and execute tool
            for t in supervisor_tools:
                if t.name == tool_name:
                    tool_result = t.invoke(tool_args)
                    tool_messages.append(ToolMessage(
                        content=tool_result,
                        tool_call_id=tool_call["id"]
                    ))
                    break
        
        return {
            "messages": [result] + tool_messages,
            **{k: v for k, v in state.items() if k != "messages"}  # Preserve other state
        }
    else:
        return {"messages": [result]}

# Build graph
checkpointer = MemorySaver()
graph = StateGraph(AgentState)

graph.add_node("supervisor", supervisor_node)
graph.add_edge(START, "supervisor")

# Loop until no more tool calls
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    return "supervisor" if isinstance(last_message, AIMessage) and last_message.tool_calls else END

graph.add_conditional_edges("supervisor", should_continue)

app = graph.compile(checkpointer=checkpointer)

# Test
config = {"configurable": {"thread_id": "1"}}
result = app.invoke(
    {"messages": [HumanMessage(content="Build a simple Flask API")]}, 
    config
)

print(result["messages"][-1].content)