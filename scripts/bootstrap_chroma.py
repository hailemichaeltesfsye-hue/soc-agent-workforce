from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from soc_agent_workforce.memory.chroma_client import get_collection


def initialize_collections() -> None:
    """Create the incident and MITRE ChromaDB collections used by the SOC workflow."""
    get_collection("incidents")
    get_collection("mitre_techniques")
    print("ChromaDB collections initialized: incidents, mitre_techniques")


if __name__ == "__main__":
    initialize_collections()
