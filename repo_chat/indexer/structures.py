from pydantic import BaseModel, ConfigDict, Field


class IndexingResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    collection_name: str
    files_seen: int = Field(ge=0)
    chunks_seen: int = Field(ge=0)
    chunks_indexed: int = Field(ge=0)
    skipped_existing_index: bool
