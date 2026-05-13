import hashlib
import re
from pathlib import Path

from api.azure_openai_client.azure_openai_client import AzureOpenAIClient
from api.azure_openai_client.instance import azure_openai_client
from api.chroma_client.chroma_client import ChromaClient
from api.chroma_client.instance import chroma_client
from repo_chat.chunks.chunking import chunk_file
from repo_chat.indexer.repository_utils import iter_repository_files
from repo_chat.indexer.structures import IndexingResult


def index_repository(
    repo_path: Path,
    openai_client: AzureOpenAIClient = azure_openai_client,
    vector_client: ChromaClient = chroma_client,
) -> IndexingResult:
    collection_name = _collection_name_for_repo(repo_path)
    collection = vector_client.get_or_create_repository_collection(
        collection_name=collection_name,
        repo_path=repo_path,
    )

    if collection.count() > 0:
        return IndexingResult(
            collection_name=collection_name,
            files_seen=0,
            chunks_seen=collection.count(),
            chunks_indexed=0,
            skipped_existing_index=True,
        )

    files_seen = 0
    chunks_seen = 0
    chunks_indexed = 0

    for file_path in iter_repository_files(repo_path):
        files_seen += 1
        chunks = chunk_file(repo_path, file_path)
        chunks_seen += len(chunks)

        for chunk in chunks:
            embedding_response = openai_client.create_embedding(chunk.content)
            embedding = embedding_response.data[0].embedding
            collection.add(
                ids=[_chunk_id(repo_path, chunk.file, chunk.start_line, chunk.end_line)],
                embeddings=[embedding],
                documents=[chunk.content],
                metadatas=[chunk.metadata()],
            )
            chunks_indexed += 1

    return IndexingResult(
        collection_name=collection_name,
        files_seen=files_seen,
        chunks_seen=chunks_seen,
        chunks_indexed=chunks_indexed,
        skipped_existing_index=False,
    )


def _collection_name_for_repo(repo_path: Path) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "-", repo_path.name).strip("-_").lower()
    if len(normalized) >= 3:
        return normalized

    digest = hashlib.sha256(str(repo_path).encode("utf-8")).hexdigest()[:8]
    return f"repo-{digest}"


def _chunk_id(repo_path: Path, file: str, start_line: int, end_line: int) -> str:
    raw_id = f"{repo_path}|{file}|{start_line}|{end_line}"
    return hashlib.sha256(raw_id.encode("utf-8")).hexdigest()
