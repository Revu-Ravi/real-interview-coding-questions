
import streamlit as st

st.set_page_config(
    page_title="LangGraph Workflow",
    page_icon="🔀",
    layout="wide",
)

st.title("IT Helpdesk — LangGraph Workflow")
st.caption(
    "Visual representation of the StateGraph defined in workflow.py"
)

st.markdown("""
This diagram represents the routing configured in the project's
LangGraph StateGraph. The workflow passes state between nodes and
uses conditional edges to select the next step.
""")

graph = r"""
digraph HelpdeskWorkflow {
    graph [
        rankdir=TB,
        bgcolor="transparent",
        pad="0.35",
        nodesep="0.55",
        ranksep="0.65",
        label="IT Helpdesk Multi-Agent System",
        labelloc="t",
        fontsize=22,
        fontname="Arial"
    ];

    node [
        shape=box,
        style="rounded,filled",
        fontname="Arial",
        fontsize=12,
        margin="0.22,0.15",
        color="#64748b",
        penwidth=1.5
    ];

    edge [
        fontname="Arial",
        fontsize=10,
        color="#64748b",
        arrowsize=0.8
    ];

    START [
        label="START",
        shape=oval,
        fillcolor="#D1FAE5",
        color="#059669"
    ];

    classify [
        label="Classify / Intent Router\nroute_node()",
        fillcolor="#DBEAFE",
        color="#2563EB"
    ];

    access [
        label="Access Check Agent\naccess_node()",
        fillcolor="#D1FAE5",
        color="#059669"
    ];

    knowledge [
        label="Knowledge Search Agent\nknowledge_node()",
        fillcolor="#FEF3C7",
        color="#D97706"
    ];

    policy [
        label="Policy / Approval Check\npolicy_node()",
        fillcolor="#EDE9FE",
        color="#7C3AED"
    ];

    ticket [
        label="Action / Ticket Agent\nticket_node()",
        fillcolor="#FCE7F3",
        color="#DB2777"
    ];

    final [
        label="Final Response\nfinal_node()",
        fillcolor="#DBEAFE",
        color="#2563EB"
    ];

    END [
        label="END",
        shape=oval,
        fillcolor="#D1FAE5",
        color="#059669"
    ];

    START -> classify;

    classify -> access [
        label="category = access"
    ];

    classify -> knowledge [
        label="other categories"
    ];

    access -> knowledge;

    knowledge -> policy;

    policy -> ticket [
        label="ticket needed AND approved",
        color="#059669"
    ];

    policy -> final [
        label="otherwise",
        color="#64748b"
    ];

    ticket -> final;

    final -> END;
}
"""

st.graphviz_chart(graph, use_container_width=True)

st.divider()

st.subheader("Node responsibilities")

st.markdown("""
| Node | Responsibility |
|---|---|
| `classify` | Categorizes the user's request |
| `access` | Runs the mock account-access check for access issues |
| `knowledge` | Searches the local support-ticket dataset |
| `policy` | Checks whether ticket creation is requested |
| `ticket` | Creates a mock ticket when the graph receives approval |
| `final` | Adds the assistant response to the message state |
""")

st.info(
    "Important: this is a visualization of the configured graph, "
    "not a live execution trace. Classification and knowledge search "
    "currently use rule-based logic and local CSV data."
)
