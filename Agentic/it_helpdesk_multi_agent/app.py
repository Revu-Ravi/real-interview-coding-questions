import argparse
from registry import REGISTRY, AGENTS
from workflow import run_helpdesk
from storage import save_run, replay_last
from evaluation import evaluate

def ask(message):
    result = run_helpdesk(message)
    if result.get("needs_approval"):
        print("\nHuman approval required before creating a ticket.")
        answer = input("Approve mock ticket creation? (y/N): ").strip().lower()
        if answer == "y":
            result = run_helpdesk(message, approved=True, session_id=result.get("session_id"))
        else:
            result["response"] += " Ticket was not created because approval was not granted."
    save_run(message, result)
    print("\nAgent:", result.get("current_agent"))
    print("Category:", result.get("category"))
    print("Response:", result.get("response"))
    if result.get("tool_results"):
        print("Tool results:", result["tool_results"])
    if result.get("ticket"):
        print("Ticket:", result["ticket"])

def main():
    parser = argparse.ArgumentParser(description="IT Helpdesk Multi-Agent Prototype")
    sub = parser.add_subparsers(dest="command", required=True)
    p_ask = sub.add_parser("ask", help="Ask one IT support question")
    p_ask.add_argument("message", nargs="+")
    sub.add_parser("agents", help="List agents and registered tools")
    sub.add_parser("eval", help="Evaluate on local golden dataset")
    sub.add_parser("replay", help="Show the last stored run")
    args = parser.parse_args()

    if args.command == "ask":
        ask(" ".join(args.message))
    elif args.command == "agents":
        print("AGENTS")
        for agent in AGENTS:
            print(f"- {agent['name']}: {agent['description']} ({', '.join(agent['capabilities'])})")
        print("\nREGISTERED TOOLS")
        for tool in REGISTRY.list_tools():
            print(f"- {tool['name']}: approval_required={tool['approval_required']}")
    elif args.command == "eval":
        result = evaluate()
        print(f"Total: {result['total']} | Correct: {result['correct']} | Grounded: {result['grounded']}")
        for row in result["details"]:
            print(f"- {'PASS' if row['correct'] else 'CHECK'}: {row['query']}")
    elif args.command == "replay":
        result = replay_last()
        print(result if result else "No saved runs yet.")

if __name__ == "__main__":
    main()
