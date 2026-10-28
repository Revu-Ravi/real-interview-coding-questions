from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).parent / "config" / "tools.yaml"

class ToolRegistry:
    def __init__(self, path=CONFIG_PATH):
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        self.tools = {item["name"]: item for item in data.get("tools", [])}

    def get(self, name):
        if name not in self.tools:
            raise KeyError(f"Tool not registered: {name}")
        return self.tools[name]

    def list_tools(self):
        return list(self.tools.values())

REGISTRY = ToolRegistry()

AGENTS = [
    {"name": "Knowledge Search Agent", "description": "Finds a likely resolution from the local ticket dataset.", "capabilities": ["search", "retrieval"], "version": "1.0"},
    {"name": "Access Check Agent", "description": "Checks mock account/access status.", "capabilities": ["access", "account"], "version": "1.0"},
    {"name": "Reasoning Agent", "description": "Chooses next steps and checks whether a ticket is needed.", "capabilities": ["planning", "policy"], "version": "1.0"},
    {"name": "Action/Ticket Agent", "description": "Creates a mock ticket after approval.", "capabilities": ["ticket", "action"], "version": "1.0"},
]
