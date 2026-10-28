
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import chromadb


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

ROOT = Path(__file__).parent
CHROMA_PATH = ROOT / "chroma_db"
LEGACY_RUNS = ROOT / "sessions.jsonl"

client = chromadb.PersistentClient(path=str(CHROMA_PATH))

collection = client.get_or_create_collection(
    name="helpdesk_sessions",
    embedding_function=None,
)


# --------------------------------------------------
# 2. Helper functions
# --------------------------------------------------

def _now():
    return datetime.now(timezone.utc).isoformat()


def _make_metadata(record):
    """Create ChromaDB metadata, including LLM token usage."""
    return {
        "session_id": str(record.get("session_id") or ""),
        "message": str(record.get("message") or ""),
        "category": str(record.get("category") or ""),
        "needs_approval": bool(record.get("needs_approval", False)),
        "created_at": str(record.get("created_at") or _now()),

        # Separate numeric metadata fields
        "input_tokens": int(record.get("input_tokens", 0) or 0),
        "output_tokens": int(record.get("output_tokens", 0) or 0),
        "total_tokens": int(record.get("total_tokens", 0) or 0),

        # LLM response time, in seconds
        "response_time_seconds": float(
            record.get("response_time_seconds", 0.0) or 0.0
        ),
    }


def _save_record(record, record_id=None):
    """Save a conversation record and its metadata to ChromaDB."""
    record = dict(record)

    record.setdefault("run_id", str(uuid4()))
    record.setdefault("created_at", _now())

    if not record.get("session_id"):
        record["session_id"] = str(uuid4())

    # Ensure consistent token fields for old and new records.
    record.setdefault("input_tokens", 0)
    record.setdefault("output_tokens", 0)
    record.setdefault("total_tokens", 0)
    record.setdefault("response_time_seconds", 0.0)

    if record_id is None:
        record_id = record["run_id"]

    # Placeholder vectors are for storage only, not semantic search.
    collection.upsert(
        ids=[record_id],
        documents=[json.dumps(record, ensure_ascii=False)],
        metadatas=[_make_metadata(record)],
        embeddings=[[0.0] * 384],
    )

    return record


def _decode_documents(documents):
    """Convert stored JSON documents into dictionaries."""
    records = []

    for document in documents or []:
        if not document:
            continue

        try:
            records.append(json.loads(document))
        except json.JSONDecodeError:
            continue

    return records


# --------------------------------------------------
# 3. Save a conversation interaction
# --------------------------------------------------

def save_run(message, result):
    """
    Save a user query, response, and LLM usage.

    Expected optional result fields:
      input_tokens
      output_tokens
      total_tokens
      response_time_seconds
    """
    # Also accept a nested usage dictionary, if supplied.
    usage = result.get("token_usage") or {}

    input_tokens = int(
        result.get("input_tokens", usage.get("input_tokens", 0)) or 0
    )
    output_tokens = int(
        result.get("output_tokens", usage.get("output_tokens", 0)) or 0
    )
    total_tokens = int(
        result.get(
            "total_tokens",
            usage.get("total_tokens", input_tokens + output_tokens),
        ) or 0
    )

    record = {
        "run_id": str(uuid4()),
        "session_id": result.get("session_id") or str(uuid4()),
        "message": message,
        "response": result.get("response", ""),
        "category": result.get("category", ""),
        "tool_results": result.get("tool_results", {}),
        "ticket": result.get("ticket"),
        "needs_approval": result.get("needs_approval", False),

        # Token usage saved as separate fields
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "response_time_seconds": float(
            result.get(
                "response_time_seconds",
                usage.get("response_time_seconds", 0.0),
            ) or 0.0
        ),
        "created_at": _now(),
    }

    return _save_record(record)


# --------------------------------------------------
# 4. Load all conversation records
# --------------------------------------------------

def load_runs():
    """Return all records, newest first."""
    data = collection.get(include=["documents"])

    records = _decode_documents(data.get("documents", []))
    records.sort(
        key=lambda record: record.get("created_at", ""),
        reverse=True,
    )

    return records


# --------------------------------------------------
# 5. Retrieve records by session ID
# --------------------------------------------------

def get_conversation_by_session_id(session_id):
    """Retrieve every record matching a session ID."""
    if not session_id or not session_id.strip():
        return []

    data = collection.get(
        where={"session_id": session_id.strip()},
        include=["documents"],
    )

    records = _decode_documents(data.get("documents", []))
    records.sort(key=lambda record: record.get("created_at", ""))

    return records


# --------------------------------------------------
# 6. Get all unique session IDs
# --------------------------------------------------

def get_all_session_ids():
    """Return all unique saved session IDs."""
    data = collection.get(include=["metadatas"])

    return sorted({
        metadata["session_id"]
        for metadata in data.get("metadatas", [])
        if metadata and metadata.get("session_id")
    })


# --------------------------------------------------
# 7. Replay the latest record
# --------------------------------------------------

def replay_last():
    """Return the newest saved record, if available."""
    records = load_runs()
    return records[0] if records else None


# --------------------------------------------------
# 8. Migrate records from sessions.jsonl
# --------------------------------------------------

def migrate_legacy_runs():
    """Import legacy records without deleting the original file."""
    if not LEGACY_RUNS.exists():
        return 0

    migrated = 0

    with LEGACY_RUNS.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            if not record.get("session_id"):
                continue

            record.setdefault("created_at", _now())
            record.setdefault("run_id", str(uuid4()))

            digest = hashlib.sha256(
                f"{line_number}:{line}".encode("utf-8")
            ).hexdigest()

            _save_record(record, record_id=f"legacy-{digest}")
            migrated += 1

    return migrated


# --------------------------------------------------
# 9. Import legacy records on startup
# --------------------------------------------------

migrate_legacy_runs()
