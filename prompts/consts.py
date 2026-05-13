from enum import Enum

class Prompts(str, Enum):
    RESEARCH_REPOSITORY = "research_repository"


class PromptRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
