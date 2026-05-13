# research-llm-exercise

CLI chatbot for asking questions about a local Git repository.

The app indexes repository files into a local ChromaDB vector store, retrieves relevant chunks for each question, and asks Azure OpenAI GPT-4o to answer using those chunks as context.

## Setup

### Requirements

- Python 3.12
- Poetry
- Azure OpenAI environment variables in `.env`

The app expects these variables:

```env
AZURE_OPENAI_API_VERSION=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_MODEL_GPT4o=
AZURE_OPENAI_MODEL_ADA2=
```

Authentication uses `EnvironmentCredential`, so make sure the Azure identity environment is configured for your machine/session.

### Install

```powershell
poetry install
```

Run the CLI:

```powershell
poetry run chat
```

The local vector database is stored under:

```text
vector_store/
```

Generated database files are ignored by git.

## Manual

### Interactive Chat

```powershell
poetry run chat
```

Flow:

1. The app greets you.
2. It asks for a local git repository path.
3. It indexes the repository into ChromaDB.
4. If an index already exists, it asks whether to re-index:

```text
Re-index? [y/n]
```

Use:

- `y` to delete the existing collection and index again
- `n` to use the existing local index

After indexing, ask questions about the repository:

```text
Ask a question about this repository, or type 'exit':
```

Type `exit` to end the conversation.

### Delete Index

Delete the local vector index for a repository:

```powershell
poetry run chat delete-index <repo_path>
```

Example:

```powershell
poetry run chat delete-index .
```

If an index exists, the matching ChromaDB collection is deleted. If no index exists, the CLI prints a message and exits.
