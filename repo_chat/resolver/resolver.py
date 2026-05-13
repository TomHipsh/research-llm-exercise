from pathlib import Path
from typing import List, Mapping, Optional

from api.azure_openai_client.azure_openai_client import AzureOpenAIClient
from api.chroma_client.chroma_client import ChromaClient
from repo_chat.indexer.indexing import collection_name_for_repo
from repo_chat.resolver.structures import RelevantChunk, ResolveResult


def resolve_question(
    repo_path: Path,
    question: str,
    openai_client: Optional[AzureOpenAIClient] = None,
    vector_client: Optional[ChromaClient] = None,
    n_results: int = 5,
) -> ResolveResult:
    if openai_client is None:
        from api.azure_openai_client.instance import azure_openai_client

        openai_client = azure_openai_client

    if vector_client is None:
        from api.chroma_client.instance import chroma_client

        vector_client = chroma_client

    embedding_response = openai_client.create_embedding(question)
    question_embedding = embedding_response.data[0].embedding
    query_result = vector_client.query_repository_collection(
        collection_name=collection_name_for_repo(repo_path),
        query_embedding=question_embedding,
        n_results=n_results,
    )

    if query_result is None:
        return ResolveResult(question=question, chunks=[])

    documents = query_result["documents"] or [[]]
    metadatas = query_result["metadatas"] or [[]]
    distances = query_result["distances"] or [[]]
    chunks: List[RelevantChunk] = []

    for document, metadata, distance in zip(documents[0], metadatas[0], distances[0]):
        if metadata is None:
            continue

        chunks.append(_relevant_chunk_from_query_result(document, metadata, distance))

    return ResolveResult(question=question, chunks=chunks)


def _relevant_chunk_from_query_result(
    document: str,
    metadata: Mapping[str, object],
    distance: float,
) -> RelevantChunk:
    return RelevantChunk(
        file=str(metadata["file"]),
        start_line=int(metadata["start_line"]),
        end_line=int(metadata["end_line"]),
        language=str(metadata["language"]),
        content=document,
        distance=distance,
    )
