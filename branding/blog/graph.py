from langgraph.graph import StateGraph, END
from branding.blog.state import BlogState
from branding.blog.agents.spot_fetch import spot_fetch
from branding.blog.agents.writer import writer
from branding.blog.agents.seo_geo import seo_geo
from branding.blog.agents.eval import eval_agent
from branding.blog.agents.publish import publish

MAX_REVISIONS = 3


def should_revise(state: BlogState) -> str:
    if state.get("approved"):
        return "publish"
    if state.get("revision_count", 0) >= MAX_REVISIONS:
        print(f"[Graph] 최대 재작성 횟수 도달, 강제 퍼블리시")
        return "publish"
    return "writer"


def increment_revision(state: BlogState) -> BlogState:
    return {**state, "revision_count": state.get("revision_count", 0) + 1}


def build_graph():
    g = StateGraph(BlogState)

    g.add_node("spot_fetch", spot_fetch)
    g.add_node("writer", writer)
    g.add_node("seo_geo", seo_geo)
    g.add_node("eval", eval_agent)
    g.add_node("revise", increment_revision)
    g.add_node("publish", publish)

    g.set_entry_point("spot_fetch")
    g.add_edge("spot_fetch", "writer")
    g.add_edge("writer", "seo_geo")
    g.add_edge("seo_geo", "eval")
    g.add_conditional_edges("eval", should_revise, {
        "publish": "publish",
        "writer": "revise",
    })
    g.add_edge("revise", "writer")
    g.add_edge("publish", END)

    return g.compile()
