from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection


class ChromaClient:
    """Small wrapper around the configured ChromaDB persistent client."""

    def __init__(self, vector_store_path: Path) -> None:
        self.vector_store_path = vector_store_path
        self.vector_store_path.mkdir(exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.vector_store_path))

    def get_or_create_repository_collection(
        self,
        collection_name: str,
        repo_path: Path,
    ) -> Collection:
        return self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=None,
            metadata={
                "collection_name": collection_name,
                "repository_path": str(repo_path),
            },
        )
