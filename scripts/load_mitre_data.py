from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from soc_agent_workforce.memory import add_mitre_document
from soc_agent_workforce.memory.chroma_client import get_project_root


def load_mitre_data() -> None:
    dataset_path = get_project_root() / "data" / "mitre" / "attack_techniques.json"
    with dataset_path.open("r", encoding="utf-8") as f:
        techniques = json.load(f)

    for technique in techniques:
        add_mitre_document(
            technique_id=technique["id"],
            name=technique["name"],
            tactic=technique["tactic"],
            description=technique["description"],
        )

    print(f"Loaded {len(techniques)} MITRE techniques into ChromaDB")


if __name__ == "__main__":
    load_mitre_data()
