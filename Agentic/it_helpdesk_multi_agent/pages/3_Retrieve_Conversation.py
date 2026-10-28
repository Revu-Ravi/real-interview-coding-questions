
import streamlit as st
from storage import (
    get_conversation_by_session_id,
    get_all_session_ids,
    load_runs,
)

st.set_page_config(
    page_title="Retrieve Conversation",
    page_icon="🔎",
    layout="wide",
)

st.title("Retrieve Conversation by Session ID")
st.write(
    "View saved queries, identify a session, "
    "and retrieve its conversation."
)

# Load saved records
runs = load_runs()

if not runs:
    st.info("No saved conversations found yet.")
    st.stop()

# Show saved queries, newest first
st.subheader("Saved Conversations")

for index, record in enumerate(reversed(runs)):
    sid = record.get("session_id", "")
    query = record.get("message", "No query available")

    with st.expander(
        f"Query: {query[:90]} | Session: {sid[:8]}..."
    ):
        st.write("**Session ID:**")
        st.code(sid)

        st.write("**User Query:**", query)
        st.write(
            "**Assistant Response:**",
            record.get("response", ""),
        )
        st.write("**Category:**", record.get("category", ""))

        if st.button(
            "Retrieve this session",
            key=f"retrieve_{index}_{sid}",
        ):
            st.session_state["selected_session_id"] = sid
            st.rerun()

# Manual session ID search
st.divider()
st.subheader("Retrieve by Session ID")

session_ids = get_all_session_ids()

session_id = st.text_input(
    "Enter Session ID",
    value=st.session_state.get("selected_session_id", ""),
    placeholder="Paste a session ID here",
)

if st.button("Retrieve Conversation", type="primary"):
    if not session_id.strip():
        st.warning("Please enter a session ID.")
    else:
        st.session_state["selected_session_id"] = (
            session_id.strip()
        )

# Display retrieved records
selected_id = st.session_state.get(
    "selected_session_id", ""
)

if selected_id:
    records = get_conversation_by_session_id(selected_id)

    if not records:
        st.error(
            "No conversation found for this session ID. "
            "Please check the ID and try again."
        )
    else:
        st.success(
            f"Found {len(records)} saved record(s)."
        )

        for index, record in enumerate(records, start=1):
            st.markdown(f"### Conversation Record {index}")

            st.write(
                "**Session ID:**",
                record.get("session_id"),
            )
            st.write(
                "**User Query:**",
                record.get("message"),
            )
            st.write(
                "**Assistant Response:**",
                record.get("response"),
            )
            st.write(
                "**Category:**",
                record.get("category"),
            )

            with st.expander("Agent Tool Results"):
                st.json(record.get("tool_results", {}))

            ticket = record.get("ticket")
            if ticket:
                with st.expander("Ticket Details"):
                    st.json(ticket)

            st.write(
                "**Approval Required:**",
                record.get("needs_approval", False),
            )

            st.divider()
