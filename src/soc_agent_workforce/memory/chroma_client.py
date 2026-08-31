from __future__ import annotations

from pathlib import Path

import chromadb


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_chroma_client() -> chromadb.PersistentClient:
    chroma_path = get_project_root() / ".chroma"
    chroma_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(chroma_path))


def get_collection(name: str):
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )
