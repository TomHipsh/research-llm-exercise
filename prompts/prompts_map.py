from typing import Dict

from prompts.consts import Prompts, PromptRole
from prompts.research_repository import (
    RESEARCH_REPOSITORY_SYSTEM_PROMPT,
    RESEARCH_REPOSITORY_USER_INPUT_PROMPT
)

prompts_mapper: Dict[Prompts, Dict[PromptRole, str]] = {
    Prompts.RESEARCH_REPOSITORY: {
        PromptRole.SYSTEM: RESEARCH_REPOSITORY_SYSTEM_PROMPT,
        PromptRole.USER: RESEARCH_REPOSITORY_USER_INPUT_PROMPT
    }
}
