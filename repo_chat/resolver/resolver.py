from pathlib import Path
from typing import List, Mapping, Optional

from api.azure_openai_client.azure_openai_client import AzureOpenAIClient
from api.chroma_client.chroma_client import ChromaClient
from openai.types.chat import ChatCompletionMessageParam
from prompts.consts import PromptRole, Prompts
from prompts.prompts_map import prompts_mapper
from repo_chat.indexer.indexing import collection_name_for_repo
from repo_chat.resolver.consts import DEFAULT_CHUNK_RESULTS_COUNT
from repo_chat.resolver.structures import RelevantChunk, ResolveResult


def resolve_question(
    repo_path: Path,
    question: str,
    openai_client: Optional[AzureOpenAIClient] = None,
    vector_client: Optional[ChromaClient] = None,
    n_results: int = DEFAULT_CHUNK_RESULTS_COUNT,
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
        return ResolveResult(
            question=question,
            chunks=[],
            answer="No index was found for this repository.",
        )

    documents = query_result["documents"] or [[]]
    metadatas = query_result["metadatas"] or [[]]
    distances = query_result["distances"] or [[]]
    chunks: List[RelevantChunk] = []

    for document, metadata, distance in zip(documents[0], metadatas[0], distances[0]):
        if metadata is None:
            continue

        chunks.append(_relevant_chunk_from_query_result(document, metadata, distance))

    if not chunks:
        return ResolveResult(
            question=question,
            chunks=[],
            answer="No relevant chunks were found for this question.",
        )

    answer = _answer_question_from_chunks(
        openai_client=openai_client,
        question=question,
        chunks=chunks,
    )

    return ResolveResult(question=question, chunks=chunks, answer=answer)


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


def _answer_question_from_chunks(
    openai_client: AzureOpenAIClient,
    question: str,
    chunks: List[RelevantChunk],
) -> str:
    prompt_config = prompts_mapper[Prompts.RESEARCH_REPOSITORY]
    system_prompt = prompt_config[PromptRole.SYSTEM]
    user_prompt = _render_user_prompt(
        prompt_template=prompt_config[PromptRole.USER],
        question=question,
        chunks=chunks,
    )
    messages: List[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    response = openai_client.create_chat_completion(messages=messages)
    answer = response.choices[0].message.content

    if answer is None:
        return "The model returned an empty answer."

    return answer


def _render_user_prompt(
    prompt_template: str,
    question: str,
    chunks: List[RelevantChunk],
) -> str:
    return (
        prompt_template.replace("{{user_message}}", question)
        .replace("{{retrieved_chunks}}", _format_chunks_for_prompt(chunks))
    )


def _format_chunks_for_prompt(chunks: List[RelevantChunk]) -> str:
    formatted_chunks: List[str] = []

    for index, chunk in enumerate(chunks, start=1):
        formatted_chunks.append(
            "\n".join(
                [
                    (
                        f'<chunk id="{index}" file="{chunk.file}" '
                        f'lines="{chunk.start_line}-{chunk.end_line}" '
                        f'language="{chunk.language.value}" '
                        f'distance="{chunk.distance:.4f}">'
                    ),
                    chunk.content,
                    "</chunk>",
                ]
            )
        )

    return "\n\n".join(formatted_chunks)
