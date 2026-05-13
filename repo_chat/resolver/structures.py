from typing import List

from pydantic import BaseModel, ConfigDict, Field

from repo_chat.chunks.consts import Language


class RelevantChunk(BaseModel):
    model_config = ConfigDict(frozen=True)

    file: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    language: Language
    content: str
    distance: float


class ResolveResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    question: str
    chunks: List[RelevantChunk]
    answer: str
