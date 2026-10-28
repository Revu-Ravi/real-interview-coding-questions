
from typing import TypedDict, Any
from uuid import uuid4
from datetime import datetime, timezone

from langgraph.graph import StateGraph, START, END

from agents import (
    categorize,
    knowledge_search,
    check_access,
    create_ticket,
    generate_response,
)
from observability import traced


OUT_OF_SCOPE_RESPONSE = (
    "Sorry, I don't have an answer for that question."
)

TICKET_REQUEST_PHRASES = (
    "create a ticket",
    "create ticket",
    "raise a ticket",
    "raise ticket",
    "open a ticket",
    "open ticket",
    "log a ticket",
    "log ticket",
    "submit a ticket",
    "submit ticket",
    "generate a ticket",
    "generate ticket",
    "file a ticket",
    "file ticket",
    "escalate this",
    "escalate the issue",
    "escalate my issue",
    "escalate to support",
)


class HelpdeskState(TypedDict, total=False):
    message: str
    session_id: str
    category: str
    current_agent: str
    tool_results: dict[str, Any]
    response: str
    needs_approval: bool
    approved: bool
    ticket_requested: bool
    ticket: dict[str, Any] | None
    messages: list[dict[str, str]]
    execution_events: list[dict[str, str]]
    llm_error: str | None

    # LLM usage metrics
    input_tokens: int
    output_tokens: int
    total_tokens: int
    response_time_seconds: float


def record_event(state, node, detail):
    """Record a workflow node execution."""
    events = list(state.get("execution_events", []))

    events.append({
        "node": node,
        "status": "completed",
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    return events


def is_ticket_request(message: str) -> bool:
    """Return True only when the user explicitly requests a ticket."""
    text = " ".join(message.lower().split())

    return any(
        phrase in text
        for phrase in TICKET_REQUEST_PHRASES
    )


def route_node(state: HelpdeskState):
    """Classify the issue and identify explicit ticket requests."""

    with traced(
        "agent.intent_router",
        session_id=state.get("session_id", ""),
    ):
        message = state["message"]
        category = categorize(message)
        ticket_requested = is_ticket_request(message)

        detail = (
            f"Category: {category}. "
            f"Explicit ticket request: {ticket_requested}."
        )

        if category == "access":
            detail += " Next: access check."
        else:
            detail += " Next: knowledge search."

        return {
            "category": category,
            "ticket_requested": ticket_requested,
            "current_agent": "Reasoning Agent",
            "messages": state.get("messages", [])
            + [{"role": "user", "content": message}],
            "execution_events": record_event(
                state,
                "classify",
                detail,
            ),
        }


def knowledge_node(state: HelpdeskState):
    """Search the local IT support dataset."""

    result = knowledge_search(state["message"])

    matched = bool(result.get("matched", False))

    detail = (
        f"Knowledge search completed. "
        f"Relevant match: {matched}. "
        f"Matched query: {result.get('matched_query', '')}"
    )

    return {
        "current_agent": "Knowledge Search Agent",
        "tool_results": {
            **state.get("tool_results", {}),
            "knowledge": result,
        },
        "execution_events": record_event(
            state,
            "knowledge",
            detail,
        ),
    }


def access_node(state: HelpdeskState):
    """Run the mock account access check."""

    result = check_access()

    return {
        "current_agent": "Access Check Agent",
        "tool_results": {
            **state.get("tool_results", {}),
            "access": result,
        },
        "execution_events": record_event(
            state,
            "access",
            "Mock access check completed. "
            f"Account status: "
            f"{result.get('account_status', 'unknown')}.",
        ),
    }


def route_after_knowledge(state: HelpdeskState):
    """
    Stop immediately when the CSV has no relevant result.

    Out-of-scope questions never reach response generation,
    human approval, or ticket creation.
    """
    knowledge = (
        state.get("tool_results", {}).get("knowledge", {})
    )

    if knowledge.get("matched", False):
        return "policy"

    return "out_of_scope"


def out_of_scope_node(state: HelpdeskState):
    """Return the exact fallback response and stop the workflow."""

    return {
        "current_agent": "Knowledge Search Agent",
        "response": OUT_OF_SCOPE_RESPONSE,
        "needs_approval": False,
        "ticket": None,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "response_time_seconds": 0.0,
        "execution_events": record_event(
            state,
            "out_of_scope",
            "No relevant CSV match. Stopped without LLM response "
            "generation, human approval, or ticket creation.",
        ),
    }


def policy_node(state: HelpdeskState):
    """
    Generate a response for relevant support questions.

    Ask for approval only when the user explicitly requests a ticket.
    This node never creates a ticket.
    """
    tool_results = state.get("tool_results", {})
    knowledge = tool_results.get("knowledge", {})
    access = tool_results.get("access")

    # Defence in depth: this node should only receive matched results.
    if not knowledge.get("matched", False):
        return {
            "current_agent": "Knowledge Search Agent",
            "response": OUT_OF_SCOPE_RESPONSE,
            "needs_approval": False,
            "ticket": None,
            "execution_events": record_event(
                state,
                "policy",
                "Stopped because no relevant knowledge match exists.",
            ),
        }

    resolution = knowledge.get("resolution", "")

    generated = generate_response(
        message=state["message"],
        category=state.get("category", "other"),
        resolution=resolution,
        access_result=access,
    )

    # Support both dictionary and older string return formats.
    if isinstance(generated, dict):
        response = generated.get("response", "")
        input_tokens = int(
            generated.get("input_tokens", 0) or 0
        )
        output_tokens = int(
            generated.get("output_tokens", 0) or 0
        )
        total_tokens = int(
            generated.get(
                "total_tokens",
                input_tokens + output_tokens,
            ) or 0
        )
        response_time_seconds = float(
            generated.get("response_time_seconds", 0.0) or 0.0
        )
        llm_error = generated.get("llm_error")
    else:
        response = str(generated)
        input_tokens = 0
        output_tokens = 0
        total_tokens = 0
        response_time_seconds = 0.0
        llm_error = None

    ticket_requested = state.get("ticket_requested", False)
    approved = state.get("approved", False)

    if ticket_requested and not approved:
        response += (
            "\n\n**Human approval required:** "
            "Please approve this request before the IT support "
            "ticket is created."
        )
        needs_approval = True
        detail = (
            "Support response generated. Explicit ticket request "
            "detected; waiting for human approval."
        )
    elif ticket_requested and approved:
        needs_approval = False
        detail = (
            "Support response generated. Ticket request approved; "
            "routing to ticket creation."
        )
    else:
        needs_approval = False
        detail = (
            "Support response generated. No ticket requested; "
            "no human approval required."
        )

    return {
        "current_agent": (
            "Human Approval"
            if needs_approval
            else "Response Agent"
        ),
        "response": response,
        "needs_approval": needs_approval,
        "ticket": None,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "response_time_seconds": response_time_seconds,
        **({"llm_error": llm_error} if llm_error else {}),
        "execution_events": record_event(
            state,
            "policy",
            detail,
        ),
    }


def ticket_node(state: HelpdeskState):
    """Create a mock ticket only for an explicit, approved request."""

    # Defence in depth: both conditions are mandatory.
    if (
        not state.get("approved", False)
        or not state.get("ticket_requested", False)
    ):
        return {
            "current_agent": "Human Approval",
            "ticket": None,
            "needs_approval": bool(
                state.get("ticket_requested", False)
            ),
            "execution_events": record_event(
                state,
                "ticket",
                "Ticket creation blocked: explicit request or "
                "human approval missing.",
            ),
        }

    result = create_ticket(
        state["message"],
        state.get("category", "other"),
    )

    ticket_id = (
        result.get("ticket_id", "Unknown")
        if isinstance(result, dict)
        else str(result)
    )

    return {
        "current_agent": "Action/Ticket Agent",
        "ticket": result,
        "needs_approval": False,
        "response": (
            state.get("response", "")
            + f"\n\nMock ticket created: {ticket_id}."
        ),
        "execution_events": record_event(
            state,
            "ticket",
            f"Mock ticket created after approval: {ticket_id}.",
        ),
    }


def final_node(state: HelpdeskState):
    """Record the final response and workflow completion."""

    response = state.get("response", "")

    events = record_event(
        state,
        "final",
        "Final response prepared.",
    )

    events.append({
        "node": "END",
        "status": "completed",
        "detail": "Workflow finished.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    return {
        "messages": state.get("messages", [])
        + [{"role": "assistant", "content": response}],
        "execution_events": events,
    }


def route_after_classify(state: HelpdeskState):
    """Route account-access issues through the mock access check."""

    if state.get("category") == "access":
        return "access"

    return "knowledge"


def route_after_policy(state: HelpdeskState):
    """Create a ticket only for an explicitly requested, approved action."""

    if (
        state.get("ticket_requested", False)
        and state.get("approved", False)
    ):
        return "ticket"

    return "final"


# --------------------------------------------------
# Build the LangGraph workflow
# --------------------------------------------------

graph = StateGraph(HelpdeskState)

graph.add_node("classify", route_node)
graph.add_node("knowledge", knowledge_node)
graph.add_node("access", access_node)
graph.add_node("policy", policy_node)
graph.add_node("out_of_scope", out_of_scope_node)
graph.add_node("ticket", ticket_node)
graph.add_node("final", final_node)

graph.add_edge(START, "classify")

graph.add_conditional_edges(
    "classify",
    route_after_classify,
    {
        "access": "access",
        "knowledge": "knowledge",
    },
)

graph.add_edge("access", "knowledge")

graph.add_conditional_edges(
    "knowledge",
    route_after_knowledge,
    {
        "policy": "policy",
        "out_of_scope": "out_of_scope",
    },
)

graph.add_edge("out_of_scope", "final")

graph.add_conditional_edges(
    "policy",
    route_after_policy,
    {
        "ticket": "ticket",
        "final": "final",
    },
)

graph.add_edge("ticket", "final")
graph.add_edge("final", END)

HELPDESK_GRAPH = graph.compile()


# --------------------------------------------------
# Public workflow entry point
# --------------------------------------------------

def run_helpdesk(
    message: str,
    approved: bool = False,
    session_id: str | None = None,
):
    """
    Run the IT helpdesk workflow.

    Normal support question:
        result = run_helpdesk(message)

    Explicit ticket request:
        result = run_helpdesk(
            "My VPN is failing. Please create a ticket"
        )

    Approval rerun:
        result = run_helpdesk(
            original_message,
            approved=True,
            session_id=original_session_id,
        )

    Keep the original message and session ID for the approval rerun.
    """
    return HELPDESK_GRAPH.invoke({
        "message": message,
        "session_id": session_id or str(uuid4()),
        "tool_results": {},
        "messages": [],
        "approved": approved,
        "needs_approval": False,
        "ticket_requested": is_ticket_request(message),
        "ticket": None,
        "execution_events": [],
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "response_time_seconds": 0.0,
    })
