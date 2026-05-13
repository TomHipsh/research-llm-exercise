from pydantic import BaseModel, ConfigDict, Field

from repo_chat.chunks.consts import Language


class CodeChunk(BaseModel):
    model_config = ConfigDict(frozen=True)

    content: str
    file: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    language: Language

    def metadata(self) -> dict[str, str | int]:
        return {
            "file": self.file,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "language": self.language.value,
        }
