from enum import Enum
import re


class Language(str, Enum):
    C = "c"
    CPP = "cpp"
    CSHARP = "csharp"
    CSS = "css"
    GO = "go"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    KOTLIN = "kotlin"
    MARKDOWN = "markdown"
    PHP = "php"
    PYTHON = "python"
    RUBY = "ruby"
    RUST = "rust"
    SHELL = "shell"
    TEXT = "text"
    TYPESCRIPT = "typescript"
    YAML = "yaml"


LANGUAGES_BY_SUFFIX = {
    ".c": Language.C,
    ".cc": Language.CPP,
    ".cpp": Language.CPP,
    ".cs": Language.CSHARP,
    ".css": Language.CSS,
    ".go": Language.GO,
    ".h": Language.C,
    ".hpp": Language.CPP,
    ".java": Language.JAVA,
    ".js": Language.JAVASCRIPT,
    ".jsx": Language.JAVASCRIPT,
    ".kt": Language.KOTLIN,
    ".md": Language.MARKDOWN,
    ".php": Language.PHP,
    ".py": Language.PYTHON,
    ".rb": Language.RUBY,
    ".rs": Language.RUST,
    ".sh": Language.SHELL,
    ".ts": Language.TYPESCRIPT,
    ".tsx": Language.TYPESCRIPT,
    ".yml": Language.YAML,
    ".yaml": Language.YAML,
}

BRACE_LANGUAGES = {
    Language.C,
    Language.CPP,
    Language.CSHARP,
    Language.GO,
    Language.JAVA,
    Language.JAVASCRIPT,
    Language.KOTLIN,
    Language.PHP,
    Language.RUST,
    Language.TYPESCRIPT,
}

DEFAULT_MAX_CHUNK_LINES = 300

BRACE_BLOCK_START = re.compile(
    r"^\s*(?:"
    r"(?:public|private|protected|static|final|abstract|async|export)\s+"
    r")*(?:"
    r"class|interface|enum|struct|impl|trait|func|fn|function|def|"
    r"[A-Za-z_][\w<>,\[\]\s*&:?.]*\s+[A-Za-z_]\w*\s*\("
    r")"
)
