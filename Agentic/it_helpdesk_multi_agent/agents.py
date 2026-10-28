
import csv
import re
import time
from pathlib import Path

from langchain_ollama import ChatOllama

from registry import REGISTRY
from observability import traced


DATA_PATH = (
    Path(__file__).parent
    / "data"
    / "golden_it_support_tickets.csv"
)

OUT_OF_SCOPE_RESPONSE = (
    "Sorry, I don't have an answer for that question."
)

# Local Llama 3 model through Ollama.
try:
    llm = ChatOllama(
        model="llama3:latest",
        temperature=0,
        num_predict=128,
        timeout=60,
    )
except Exception:
    llm = None


def load_tickets():
    """Load support tickets from the local CSV dataset."""
    with DATA_PATH.open(
        newline="",
        encoding="utf-8-sig",
    ) as file:
        return list(csv.DictReader(file))


def categorize(message):
    """Classify an IT support question using keyword rules."""
    text = message.lower().replace("-", " ").replace("_", " ")
    words = set(re.findall(r"[a-z0-9]+", text))

    if (
        "2fa" in words
        or "two factor" in text
        or "password" in words
        or "login" in words
        or "log in" in text
        or "sign in" in text
        or "account" in words
        or "authentication" in text
        or "access" in words
        or "locked out" in text
        or "cannot log" in text
        or "verification code" in text
        or "mfa" in words
    ):
        return "access"

    if (
        words & {
            "billing", "bill", "charged", "charge",
            "payment", "payments", "invoice", "refund",
            "subscription",
        }
        or "overcharged" in text
    ):
        return "billing"

    if any(
        term in text
        for term in [
            "wifi", "wi fi", "network", "internet",
            "connection", "router", "connectivity", "offline",
        ]
    ):
        return "network"

    if any(
        term in text
        for term in [
            "laptop", "keyboard", "screen", "hardware",
            "monitor", "battery", "mouse", "printer",
        ]
    ):
        return "hardware"

    if any(
        term in text
        for term in [
            "crash", "crashes", "crashing", "bug", "error",
            "application", "software", "app",
            "page not working", "not loading",
            "slow", "loading", "performance",
        ]
    ):
        return "software"

    if any(
        term in text
        for term in [
            "suspicious login", "unauthorized access",
            "security", "vulnerability", "hacked", "data breach",
        ]
    ):
        return "security"

    return "other"


def get_words(text):
    """Normalize text into meaningful words for CSV matching."""
    stopwords = {
        "i", "my", "the", "a", "an", "is", "it", "to",
        "for", "of", "and", "or", "but", "in", "on",
        "with", "this", "that", "can", "you", "please",
        "me", "not", "working", "help", "issue", "problem",
        "have", "has", "am", "are", "was", "were", "do",
        "does", "need", "want", "create", "ticket", "raise",
        "open", "log", "escalate", "system", "when", "try",
        "trying", "still", "just", "getting", "how", "what",
        "why", "who", "where", "would", "could", "should",
        "hello", "hi", "there", "myself", "very", "long",
        "time", "takes", "take", "taking",
    }

    words = set(re.findall(r"[a-z0-9]+", text.lower()))
    return words - stopwords


def expand_words(words):
    """Expand common IT terms and their variations."""
    expanded = set(words)

    synonym_groups = [
        {"slow", "slowness", "slowly", "lag", "lagging"},
        {"load", "loads", "loading", "loaded"},
        {"billing", "bill", "payment", "payments", "invoice"},
        {"page", "website", "portal", "webpage"},
        {"error", "failure", "failed", "failing"},
        {"login", "logins", "signin", "sign"},
        {"network", "connectivity", "connection"},
        {"crash", "crashes", "crashing"},
        {"password", "credential", "credentials"},
        {"access", "permission", "permissions"},
    ]

    for group in synonym_groups:
        if expanded & group:
            expanded.update(group)

    return expanded


def knowledge_search(query):
    """
    Search CSV tickets using category filtering and keyword overlap.

    This is keyword-based matching, not semantic vector search.
    """
    tool = REGISTRY.get("knowledge_search")

    with traced(
        "tool.knowledge_search",
        tool_name=tool["name"] if tool else "knowledge_search",
    ):
        rows = load_tickets()
        category = categorize(query)

        category_map = {
            "access": ["account_access"],
            "billing": ["billing_problem"],
            "security": ["security_concern"],
            "software": ["bug", "software_issue"],
            "network": ["network", "connectivity"],
            "hardware": ["hardware"],
        }

        allowed_types = category_map.get(category, [])

        if not allowed_types:
            return {
                "matched": False,
                "category": category,
                "resolution": "",
                "matched_query": "",
                "match_score": 0,
            }

        query_words = expand_words(get_words(query))

        if not query_words:
            return {
                "matched": False,
                "category": category,
                "resolution": "",
                "matched_query": "",
                "match_score": 0,
            }

        query_text = query.lower()
        best_ticket = None
        best_score = 0

        for row in rows:
            issue_type = row.get("issue_type", "").strip().lower()

            if issue_type not in allowed_types:
                continue

            initial_message = row.get("initial_message", "")
            product_area = row.get("product_area", "").replace("_", " ")
            resolution = row.get("resolution_summary", "")

            # Use issue description and product area for relevance.
            issue_words = expand_words(
                get_words(f"{initial_message} {product_area}")
            )

            if not issue_words:
                continue

            score = len(query_words & issue_words)

            # Recognize performance-related paraphrases.
            asks_about_slowness = any(
                phrase in query_text
                for phrase in [
                    "slow", "slowness", "long time",
                    "takes a long time", "lagging",
                    "performance", "latency",
                ]
            )

            ticket_mentions_performance = any(
                term in f"{initial_message} {product_area} {resolution}".lower()
                for term in [
                    "slow", "slowness", "performance",
                    "latency", "load time", "loading", "lag",
                ]
            )

            if asks_about_slowness and ticket_mentions_performance:
                score += 2

            # Prefer the ticket with the strongest evidence.
            if score > best_score:
                best_score = score
                best_ticket = row

        # Require actual overlapping evidence. A category alone is
        # not sufficient to claim that a relevant ticket was found.
        if best_ticket is not None and best_score >= 2:
            return {
                "matched": True,
                "category": category,
                "resolution": best_ticket.get(
                    "resolution_summary", ""
                ),
                "matched_query": best_ticket.get(
                    "initial_message", ""
                ),
                "match_score": best_score,
            }

        return {
            "matched": False,
            "category": category,
            "resolution": "",
            "matched_query": "",
            "match_score": best_score,
        }


def check_access(username="demo.user"):
    """Mock tool for checking account access."""
    tool = REGISTRY.get("check_access")

    with traced(
        "tool.check_access",
        tool_name=tool["name"] if tool else "check_access",
    ):
        return {
            "username": username,
            "account_status": "active (mock)",
            "access_status": "needs verification",
        }


def create_ticket(summary, category):
    """Create a mock IT support ticket."""
    tool = REGISTRY.get("create_ticket")

    with traced(
        "tool.create_ticket",
        tool_name=tool["name"] if tool else "create_ticket",
        category=category,
    ):
        return {
            "ticket_id": "MOCK-1001",
            "status": "created",
            "summary": summary,
            "category": category,
        }


def generate_response(
    message,
    category,
    resolution,
    access_result=None,
):
    """Generate an IT support response using Llama 3."""
    fallback = (
        f"Your request has been classified as '{category}'. "
        f"Support guidance: {resolution}"
    )

    if access_result:
        fallback += (
            f" Account status: "
            f"{access_result.get('account_status', 'unknown')}. "
            f"Access status: "
            f"{access_result.get('access_status', 'unknown')}."
        )

    if llm is None:
        return {
            "response": fallback,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "response_time_seconds": 0.0,
        }

    prompt = f"""
You are an IT helpdesk assistant.

User issue:
{message}

Classified category:
{category}

Verified matching CSV support resolution:
{resolution}

Mock access-check result:
{access_result or "Not applicable"}

Instructions:
- Answer in clear, simple English.
- Use the supplied CSV resolution as the source of truth.
- Give practical steps supported by that resolution.
- Do not invent fixes, policies, account details, or actions.
- Do not claim mock access was verified or changed.
- Do not claim that a ticket was created.
- Never ask for passwords or verification codes.
"""

    start_time = time.perf_counter()

    try:
        with traced(
            "agent.llama3_response",
            model="llama3:latest",
        ):
            result = llm.invoke(prompt)

        elapsed = round(time.perf_counter() - start_time, 3)

        usage = getattr(result, "usage_metadata", None) or {}
        metadata = getattr(result, "response_metadata", None) or {}

        input_tokens = int(
            usage.get(
                "input_tokens",
                metadata.get("prompt_eval_count", 0),
            ) or 0
        )

        output_tokens = int(
            usage.get(
                "output_tokens",
                metadata.get("eval_count", 0),
            ) or 0
        )

        total_tokens = int(
            usage.get(
                "total_tokens",
                input_tokens + output_tokens,
            ) or 0
        )

        answer = (result.content or "").strip() or fallback

        return {
            "response": answer,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "response_time_seconds": elapsed,
        }

    except Exception as exc:
        elapsed = round(time.perf_counter() - start_time, 3)

        return {
            "response": fallback,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "response_time_seconds": elapsed,
            "llm_error": str(exc),
        }
