"""🧠 MemoryEngineBot – wrapper for long-term memory operations."""
import json
from pathlib import Path
from typing import Dict

MEM_FILE = Path("data/memory/long_term.json")
MEM_FILE.parent.mkdir(parents=True, exist_ok=True)

class MemoryEngineBot:
    status = "ready"
    capabilities = ["read_memory", "write_memory"]

    def read(self, key: str) -> str | None:
        data: Dict = self._load()
        return data.get(key)

    def write(self, key: str, value: str):
        data = self._load()
        data[key] = value
        MEM_FILE.write_text(json.dumps(data, indent=2))

    def _load(self) -> Dict:
        if MEM_FILE.exists():
            return json.loads(MEM_FILE.read_text())
        return {}


def memory_engine_agent():
    return MemoryEngineBot()