from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from langsmith import traceable


def _get_dataset_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "mitre" / "attack_techniques.json"


def _load_dataset() -> list[dict[str, Any]]:
    dataset_path = _get_dataset_path()
    if not dataset_path.exists():
        return []
    with dataset_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@traceable(name="tool_lookup_mitre_technique")
def lookup_mitre_technique(
    technique_id: str | None = None,
    keyword: str | None = None,
    tactic: str | None = None,
    technique_name: str | None = None,
) -> dict[str, Any]:
    """Lookup a MITRE ATT&CK technique by ID, keyword, tactic, or name.

    This reads the local dataset bundled in the repository and returns the first
    matching technique with its ID, name, tactic, and description.
    """
    dataset = _load_dataset()
    if not dataset:
        return {
            "id": None,
            "name": None,
            "tactic": None,
            "description": None,
            "status": "not_found",
            "message": "MITRE dataset not found.",
        }

    search_terms: list[str] = []
    if technique_id:
        search_terms.append(technique_id)
    if technique_name:
        search_terms.append(technique_name)
    if tactic:
        search_terms.append(tactic)
    if keyword:
        search_terms.append(keyword)

    normalized_terms = [term.strip().lower() for term in search_terms if term and term.strip()]
    if not normalized_terms:
        return {
            "id": None,
            "name": None,
            "tactic": None,
            "description": None,
            "status": "invalid_query",
            "message": "Provide a technique_id, technique_name, tactic, or keyword.",
        }

    for item in dataset:
        values = [
            str(item.get("id", "")),
            str(item.get("name", "")),
            str(item.get("tactic", "")),
            str(item.get("description", "")),
        ]
        joined = " ".join(values).lower()

        match = False
        for term in normalized_terms:
            if term in joined:
                match = True
                break

        if match:
            return {
                "id": item.get("id"),
                "name": item.get("name"),
                "tactic": item.get("tactic"),
                "description": item.get("description"),
                "status": "ok",
                "message": "MITRE technique found.",
            }

    return {
        "id": None,
        "name": None,
        "tactic": None,
        "description": None,
        "status": "not_found",
        "message": "No MITRE technique matched the query.",
    }
