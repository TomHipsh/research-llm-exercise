from pathlib import Path
from typing import Optional, Sequence

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.api.types import QueryResult
from chromadb.errors import NotFoundError


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

    def get_repository_collection(self, collection_name: str) -> Optional[Collection]:
        try:
            return self.client.get_collection(
                name=collection_name,
                embedding_function=None,
            )
        except NotFoundError:
            return None

    def delete_repository_collection(self, collection_name: str) -> bool:
        if self.get_repository_collection(collection_name) is None:
            return False

        self.client.delete_collection(name=collection_name)
        return True

    def query_repository_collection(
        self,
        collection_name: str,
        query_embedding: Sequence[float],
        n_results: int,
    ) -> Optional[QueryResult]:
        collection = self.get_repository_collection(collection_name)
        if collection is None:
            return None

        return collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
