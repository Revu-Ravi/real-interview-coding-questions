# IT Helpdesk Multi-Agent Prototype

A small, runnable prototype for the HCL IT Helpdesk task. It uses LangGraph, a YAML tool registry,
simple policy/HITL, local session capture, deterministic replay, a basic evaluation runner,
OpenTelemetry console spans, CLI, and Streamlit UI.

## Setup (Windows)

```bat
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bat
python app.py ask "I cannot access my account"
python app.py ask "My laptop Wi-Fi is not working"
python app.py agents
python app.py eval
python app.py replay
streamlit run dashboard.py
```

For a ticket-creation request, the CLI asks for human approval before creating a mock ticket.
No real account, ticketing system, or external LLM is required; this keeps the demo easy to run.
The `data/golden_it_support_tickets.csv` file is a tiny sample. Replace it with the provided golden
dataset for the actual evaluation. The prototype uses keyword-based routing and retrieval so it runs
without API keys; the LLM provider can be added later behind the agent functions.
