from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from app.models.schemas import UserContext, AgentResult
from app.agents import qa, learning, quiz, research

class State(TypedDict, total=False):
    query: str
    intent: str
    course_id: str | None
    user: UserContext
    result: AgentResult

KEYWORDS = {
    "quiz": ("quiz", "test me", "questions", "practice exam"),
    "research": ("research idea", "research gap", "project idea", "novel", "literature gap"),
    "learn": ("teach me", "learn", "learning path", "study plan", "resources"),
}

def route(state: State) -> str:
    if state.get("intent") in {"qa","learn","quiz","research"}:
        return state["intent"]
    q = state["query"].lower()
    for intent, keys in KEYWORDS.items():
        if any(k in q for k in keys): return intent
    return "qa"

async def qa_node(s: State): return {"result": await qa.run(s["query"], s["user"], s.get("course_id")), "intent":"qa"}
async def learn_node(s: State): return {"result": await learning.run(s["query"], s["user"], s.get("course_id")), "intent":"learn"}
async def quiz_node(s: State): return {"result": await quiz.run(s["query"], s["user"], s.get("course_id")), "intent":"quiz"}
async def research_node(s: State): return {"result": await research.run(s["query"], s["user"], s.get("course_id")), "intent":"research"}

def build_graph():
    g=StateGraph(State)
    for name,node in {"qa":qa_node,"learn":learn_node,"quiz":quiz_node,"research":research_node}.items():
        g.add_node(name,node); g.add_edge(name,END)
    g.add_conditional_edges(START, route, {"qa":"qa","learn":"learn","quiz":"quiz","research":"research"})
    return g.compile()

graph = build_graph()
