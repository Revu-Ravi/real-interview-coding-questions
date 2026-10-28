
import streamlit as st
import pandas as pd

from workflow import run_helpdesk
from storage import (
    save_run,
    load_runs,
    get_conversation_by_session_id,
    get_all_session_ids,
)
from registry import AGENTS, REGISTRY
from evaluation import evaluate


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="IT Helpdesk Multi-Agent System",
    page_icon="🎧",
    layout="wide",
)

st.title("🎧 IT Helpdesk Multi-Agent System")
st.caption(
    "AI-powered IT support using LangGraph, Ollama Llama 3, "
    "CSV-based knowledge retrieval, and ChromaDB."
)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def safe_value(value, default="Not available"):
    """Convert missing or empty values into readable text."""
    if value is None or value == "":
        return default
    return value


def display_json(data):
    """Display dictionaries and lists in a readable format."""
    if isinstance(data, (dict, list, tuple)):
        st.json(data)
    else:
        st.write(safe_value(data))


def get_metric(result, key, default=0):
    """Safely retrieve a numeric metric."""
    try:
        return result.get(key, default) or default
    except (AttributeError, TypeError):
        return default


def get_ticket_id(ticket):
    """Return a readable ticket ID."""
    if not isinstance(ticket, dict) or not ticket:
        return "Not created"

    return str(
        ticket.get("ticket_id")
        or ticket.get("id")
        or "Created"
    )


def show_result(result):
    """Display the workflow response, metrics, trace, and evaluation."""

    st.subheader("Helpdesk Response")

    session_id = result.get("session_id")
    if session_id:
        st.caption(f"Session ID: `{session_id}`")

    response = result.get(
        "response",
        "No response was returned.",
    )
    st.markdown(response)

    # Approval status
    if result.get("needs_approval", False):
        st.warning(
            "Human approval is required before creating the ticket."
        )
    elif result.get("ticket"):
        st.success("The mock ticket was created after approval.")

    st.divider()
    st.subheader("LLM Usage and Performance")

    input_tokens = int(get_metric(result, "input_tokens"))
    output_tokens = int(get_metric(result, "output_tokens"))
    total_tokens = int(get_metric(result, "total_tokens"))
    response_time = float(
        get_metric(result, "response_time_seconds", 0.0)
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Input Tokens", f"{input_tokens:,}")
    col2.metric("Output Tokens", f"{output_tokens:,}")
    col3.metric("Total Tokens", f"{total_tokens:,}")
    col4.metric("Response Time", f"{response_time:.2f} sec")

    if result.get("llm_error"):
        st.warning(
            "The LLM encountered an error. A fallback response may "
            "have been returned."
        )
        st.code(str(result["llm_error"]))

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Category",
            str(result.get("category", "Unknown")).title(),
        )

    with col2:
        st.metric(
            "Current Agent",
            str(result.get("current_agent", "Helpdesk")),
        )

    with col3:
        st.metric(
            "Ticket",
            get_ticket_id(result.get("ticket")),
        )

    # Tool results
    with st.expander("Tool Results", expanded=False):
        display_json(result.get("tool_results", {}))

    # Execution trace
    execution_events = result.get("execution_events", [])

    # Compatibility with older workflow versions.
    if not execution_events:
        execution_events = (
            result.get("execution_trace")
            or result.get("events")
            or []
        )

    with st.expander("Execution Trace", expanded=True):
        if execution_events:
            st.dataframe(
                pd.DataFrame(execution_events),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info(
                "No execution events were returned. Check the terminal "
                "for observability logs."
            )

    # Response evaluation
    st.subheader("Response Evaluation")

    try:
        evaluation_result = evaluate(result)
        display_json(evaluation_result)
    except Exception as exc:
        st.info(
            "Evaluation could not be displayed. "
            "Check that evaluate() accepts the workflow result."
        )
        st.caption(str(exc))


def save_workflow_result(message, result):
    """Save a workflow result without breaking the dashboard."""
    try:
        saved_record = save_run(message, result)
        return saved_record if isinstance(saved_record, dict) else {}
    except Exception as exc:
        st.warning(f"The workflow completed, but saving failed: {exc}")
        return {}


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {
    "last_result": None,
    "last_message": "",
    "pending_approval": False,
    "pending_message": "",
    "pending_session_id": None,
    "approval_processing": False,
}

for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.header("System Information")

    st.write("**LLM:** Ollama — `llama3:latest`")
    st.write("**Workflow:** LangGraph")
    st.write("**Knowledge Source:** Local CSV dataset")
    st.write("**Vector Store:** ChromaDB")
    st.write("**Observability:** OpenTelemetry-style spans")

    st.divider()
    st.subheader("Registered Agents")

    try:
        display_json(AGENTS)
    except Exception:
        st.caption("Agent registry is available in registry.py.")

    st.subheader("Registered Tools")

    try:
        display_json(REGISTRY)
    except Exception:
        st.caption("Tool registry is available in registry.py.")


# --------------------------------------------------
# NEW HELP DESK REQUEST
# --------------------------------------------------

st.header("Submit an IT Support Request")

with st.form("helpdesk_request_form"):
    message = st.text_area(
        "Describe your IT issue",
        placeholder=(
            "Example: My software application keeps crashing "
            "when I try to open it."
        ),
        height=120,
    )

    submitted = st.form_submit_button(
        "Analyze and Generate Response",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not message.strip():
        st.warning("Please enter an IT issue before submitting.")
    else:
        cleaned_message = message.strip()

        try:
            with st.spinner(
                "Analyzing the issue and generating a response..."
            ):
                result = run_helpdesk(cleaned_message)

            st.session_state.last_result = result
            st.session_state.last_message = cleaned_message

            saved_record = save_workflow_result(
                cleaned_message,
                result,
            )

            # Keep the same session and original message for approval.
            session_id = (
                result.get("session_id")
                or saved_record.get("session_id")
            )

            st.session_state.pending_message = cleaned_message
            st.session_state.pending_session_id = session_id
            st.session_state.pending_approval = bool(
                result.get("needs_approval", False)
            )
            st.session_state.approval_processing = False

            if st.session_state.pending_approval:
                st.info(
                    "Response generated. Approve the ticket request "
                    "below if you want to create a ticket."
                )
            else:
                st.success("Request processed successfully.")

        except Exception as exc:
            st.error("The request could not be processed.")
            st.exception(exc)


# --------------------------------------------------
# TICKET APPROVAL
# --------------------------------------------------

if st.session_state.pending_approval:
    st.divider()
    st.subheader("Human Approval")

    st.warning(
        "The user explicitly requested a ticket. "
        "A ticket will be created only after approval."
    )

    if st.session_state.pending_session_id:
        st.caption(
            "Approval session ID: "
            f"`{st.session_state.pending_session_id}`"
        )

    approve_col, cancel_col = st.columns(2)

    with approve_col:
        approve_clicked = st.button(
            "Approve and Create Ticket",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.approval_processing,
        )

    with cancel_col:
        cancel_clicked = st.button(
            "Cancel Approval",
            use_container_width=True,
            disabled=st.session_state.approval_processing,
        )

    if approve_clicked:
        st.session_state.approval_processing = True

        try:
            with st.spinner(
                "Processing approval and creating the mock ticket..."
            ):
                result = run_helpdesk(
                    st.session_state.pending_message,
                    approved=True,
                    session_id=st.session_state.pending_session_id,
                )

            st.session_state.last_result = result

            save_workflow_result(
                st.session_state.pending_message,
                result,
            )

            # Clear approval state after the approval rerun.
            # This prevents the same UI approval action from being
            # offered again after a successful ticket creation.
            st.session_state.pending_approval = bool(
                result.get("needs_approval", False)
            )

            if not st.session_state.pending_approval:
                st.session_state.pending_message = ""
                st.session_state.pending_session_id = None

            st.session_state.approval_processing = False

            if result.get("ticket"):
                st.success("Ticket created after approval.")
            else:
                st.info(
                    "Approval workflow completed, but no ticket "
                    "was returned. Review the workflow result."
                )

            st.rerun()

        except Exception as exc:
            st.session_state.approval_processing = False
            st.error("Approval processing failed.")
            st.exception(exc)

    if cancel_clicked:
        st.session_state.pending_approval = False
        st.session_state.pending_message = ""
        st.session_state.pending_session_id = None
        st.session_state.approval_processing = False

        st.info("Approval cancelled. No ticket was created.")
        st.rerun()


# --------------------------------------------------
# DISPLAY CURRENT RESULT
# --------------------------------------------------

if st.session_state.last_result:
    st.divider()
    show_result(st.session_state.last_result)


# --------------------------------------------------
# SAVED RUNS
# --------------------------------------------------

st.divider()
st.header("Saved Helpdesk Runs")

try:
    saved_runs = load_runs()

    if saved_runs:
        st.caption(f"Stored records: {len(saved_runs)}")

        recent_runs = list(reversed(saved_runs))
        table_rows = []

        for run in recent_runs:
            if not isinstance(run, dict):
                continue

            table_rows.append({
                "Created At": run.get("created_at", ""),
                "Session ID": run.get("session_id", ""),
                "Issue": run.get("message", ""),
                "Category": run.get("category", ""),
                "Input Tokens": run.get("input_tokens", 0),
                "Output Tokens": run.get("output_tokens", 0),
                "Total Tokens": run.get("total_tokens", 0),
                "Response Time (sec)": run.get(
                    "response_time_seconds", 0.0
                ),
                "Ticket": get_ticket_id(run.get("ticket")),
            })

        if table_rows:
            st.dataframe(
                pd.DataFrame(table_rows),
                use_container_width=True,
                hide_index=True,
            )

        with st.expander("View Saved Run Details"):
            for index, run in enumerate(recent_runs):
                if not isinstance(run, dict):
                    continue

                title = (
                    f"{run.get('created_at', 'Unknown time')} — "
                    f"{str(run.get('message', 'No issue'))[:70]}"
                )

                with st.expander(title, expanded=False):
                    st.write("**Session ID**")
                    st.code(
                        str(run.get("session_id", "Not available"))
                    )

                    st.write("**Issue**")
                    st.write(run.get("message", "No issue saved."))

                    st.write("**Response**")
                    st.write(
                        run.get("response", "No response saved.")
                    )

                    st.write("**Category**")
                    st.write(run.get("category", "Unknown"))

                    st.write("**Ticket**")
                    display_json(run.get("ticket"))

                    st.write("**Token Metrics**")
                    display_json({
                        "input_tokens": run.get("input_tokens", 0),
                        "output_tokens": run.get("output_tokens", 0),
                        "total_tokens": run.get("total_tokens", 0),
                        "response_time_seconds": run.get(
                            "response_time_seconds", 0.0
                        ),
                    })

                    st.write("**Execution Events**")
                    display_json(run.get("execution_events", []))

    else:
        st.info(
            "No saved helpdesk runs were found. "
            "Submit an issue to begin."
        )

except Exception as exc:
    st.error("Could not load saved runs.")
    st.exception(exc)


# --------------------------------------------------
# CONVERSATION LOOKUP
# --------------------------------------------------

st.divider()
st.header("Retrieve Conversation")

try:
    session_ids = get_all_session_ids()

    if session_ids:
        selected_session = st.selectbox(
            "Select a session ID",
            options=session_ids,
        )

        if st.button("Retrieve Selected Conversation"):
            conversation = get_conversation_by_session_id(
                selected_session
            )

            if conversation:
                st.success("Conversation retrieved.")
                display_json(conversation)
            else:
                st.info(
                    "No records were found for this session."
                )
    else:
        st.info(
            "No session IDs are available yet. "
            "Submit an issue first."
        )

except Exception as exc:
    st.warning(
        "Conversation lookup is not available with the current "
        "storage setup."
    )
    st.caption(str(exc))


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption(
    "IT Helpdesk Multi-Agent System | Local Llama 3 inference | "
    "Token metrics are model usage counts, not cloud billing."
)
