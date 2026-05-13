# AI_COLLABARATION

This file documents how the application was shaped through collaboration with AI assistance.

## Initial Request

The chat started with this brief:

> Hi lets start
> I want to create a CLI application
> this app will be a chatbot it will recieve a git repository local path
> it should then be able to answer question about the codebase
> such as: What does the auth module do?
>
> technical flow:
> * CLI
> * load local repo files
> * chunk files into small text blocks
> * create embeddings
> * store in local vector DB
> * user asks question
> * retrieve relevant chunks
> * send chunks + question to LLM
> * answer with file references
>
> setup:
> language: Python
> CLI: Typer
> repo reading: pathlib + gitignore-parser
> emmbeddings: Ada2 via azure open ai
> vector DB: ChromaDB
> LLM: GPT 4o via azure open ai
>
> this repo already has an azure oepn ai client config
> lets start by setting this repo with a new poetry venv

## Conversation Examples

### Project Setup

User:

> lets start by setting this repo with a new poetry venv

Assistant:

> Created a Poetry project, configured an in-repo `.venv`, added the initial CLI dependencies, and verified the `chat` script.

Outcome:

- Added `pyproject.toml`
- Added `poetry.lock`
- Added `poetry.toml`
- Created the initial Typer CLI package

### Azure OpenAI Client Refactor

User:

> take the connection setup in main.py
> create a new folder: api
> under it create a new folder: azure_openai_client
> under it create a file new azure_openai_client.py it should contain a new class of the client
> and add another file named: instance.py which will contain a new global instance of the client class for the app

Assistant:

> Moved Azure OpenAI setup into a reusable client class and exposed a global instance for the app.

Outcome:

- Added `api/azure_openai_client/azure_openai_client.py`
- Added `api/azure_openai_client/instance.py`

### Error Found: Deleted Files Were Restored

User:

> do not restore the requiremnets file I deleted it
> and deleted main.py as well
> add to cli.py main() so it will be the initial startup of the app

What happened:

- The assistant had restored `requirements.txt` even though the user intentionally deleted it.
- The user caught the mistake.

Fix:

- Left `requirements.txt` and `main.py` deleted.
- Added `main()` to `repo_chat/cli.py`.
- Updated the Poetry script to point to `repo_chat.cli:main`.

### Error Found: Bytecode Cache Files

User:

> remove the pyc cahce files, its not a c-python app

What happened:

- Verification commands created `__pycache__` and `.pyc` files.
- The user called out that these should not remain in the repo.

Fix:

- Removed generated `__pycache__`, `.pyc`, and `.pyo` files.
- Later verification steps used `python -B` where possible.
- Repeated cleanup checks were performed after commands that imported Python packages.

### Error Found: Loose SDK Typing

User:

> avoid using Any typing, try to fund types for the SDK entities

What happened:

- The Azure OpenAI wrapper initially returned `Any`.

Fix:

- Replaced `Any` with OpenAI SDK types:
  - `ChatCompletion`
  - `ChatCompletionMessageParam`
  - `CreateEmbeddingResponse`

### Indexing Flow

User:

> lets start working on the indexing phase

Assistant:

> Added repository traversal, code-aware chunking, embeddings through Azure Ada2, and ChromaDB persistence.

Outcome:

- Added chunking logic
- Added indexer logic
- Added ChromaDB client wrapper
- Added local `vector_store`
- Skipped files covered by `.gitignore`

### Error Found: Duplicate Chunk Ranges

User:

> in _chunks_from_structural_ranges
> i can see that there is a duplication
> there are line ranges chucks which been saved however another chunk of the full line range in been saced as well

What happened:

- Structural ranges could overlap.
- Example: a class range and method ranges inside that class could both be saved.

Fix:

- Added `_normalize_structural_ranges`.
- Nested and overlapping ranges are now merged before chunks are created.

### Resolver Flow

User:

> add to it a file which handles the embedding logic of the user input and queries the vector db for the relevant chunks

Assistant:

> Added a resolver package that embeds the user question and queries Chroma for relevant chunks.

Outcome:

- Added `repo_chat/resolver`
- Added retrieval result structures
- Added Chroma query support

### Prompt and Answer Generation

User:

> I added new propmts folder with 2 prompts to explore the user question based on the chunks
> add additional logic steps to the resolver:
> * use the user input question and relevant chunks as context for the prompt
> * use the azure openai client gpt model to get chat completion result of it
> * return the result to the CLI and present it to the user

Assistant:

> Wired the resolver to render the prompt with retrieved chunks, call GPT-4o, and return the answer to the CLI.

Outcome:

- Prompt rendering uses the user question and retrieved chunks.
- GPT result is returned as `ResolveResult.answer`.
- CLI prints the final answer.

### Conversation Loop

User:

> now in the CLI change the conversation to an endless questios loop unless a special text is been inserted: exit

Assistant:

> Added an interactive question loop after indexing.

Outcome:

- The user can ask repeated questions.
- Typing `exit` ends the session.

## Collaboration Notes

- The user actively reviewed implementation details and corrected direction when assumptions were wrong.
- The assistant implemented changes incrementally and verified behavior with syntax checks, CLI checks, and fake-client smoke tests.
