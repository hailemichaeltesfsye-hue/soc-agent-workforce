from __future__ import annotations

from typing import Any

from sentence_transformers import SentenceTransformer

from .chroma_client import get_collection

_EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def _embed_text(text: str) -> list[float]:
    embedding = _EMBEDDING_MODEL.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def retrieve_similar_incidents(query: str, k: int = 5) -> list[dict[str, Any]]:
    """Return the k most similar incident records for the provided query text."""
    collection = get_collection("incidents")
    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[_embed_text(query)],
        n_results=min(k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    formatted: list[dict[str, Any]] = []
    for idx, doc in enumerate(results.get("documents", [[]])[0]):
        formatted.append(
            {
                "id": results.get("ids", [[]])[0][idx],
                "document": doc,
                "metadata": results.get("metadatas", [[]])[0][idx],
                "distance": results.get("distances", [[]])[0][idx],
            }
        )
    return formatted


def retrieve_mitre_context(query: str, k: int = 5) -> list[dict[str, Any]]:
    """Return the k most relevant MITRE ATT&CK technique records for the query."""
    collection = get_collection("mitre_techniques")
    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[_embed_text(query)],
        n_results=min(k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    formatted: list[dict[str, Any]] = []
    for idx, doc in enumerate(results.get("documents", [[]])[0]):
        formatted.append(
            {
                "id": results.get("ids", [[]])[0][idx],
                "document": doc,
                "metadata": results.get("metadatas", [[]])[0][idx],
                "distance": results.get("distances", [[]])[0][idx],
            }
        )
    return formatted


def add_incident_document(
    incident_id: str,
    title: str,
    summary: str,
    severity: str,
    indicators: list[str] | None = None,
    tactic: str | None = None,
) -> str:
    collection = get_collection("incidents")
    payload = {
        "incident_id": incident_id,
        "title": title,
        "summary": summary,
        "severity": severity,
        "indicators": indicators or [],
        "tactic": tactic,
    }

    combined_text = " ".join(
        filter(
            None,
            [
                title,
                summary,
                severity,
                tactic or "",
                " ".join(indicators or []),
            ],
        )
    )
    collection.add(
        ids=[incident_id],
        documents=[combined_text],
        embeddings=[_embed_text(combined_text)],
        metadatas=[payload],
    )
    return incident_id


def add_mitre_document(technique_id: str, name: str, tactic: str, description: str) -> str:
    collection = get_collection("mitre_techniques")
    text = f"{technique_id} {name} {tactic} {description}"
    metadata = {
        "technique_id": technique_id,
        "name": name,
        "tactic": tactic,
        "description": description,
    }
    collection.add(
        ids=[technique_id],
        documents=[text],
        embeddings=[_embed_text(text)],
        metadatas=[metadata],
    )
    return technique_id
