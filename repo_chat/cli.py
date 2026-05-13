from pathlib import Path

import typer


app = typer.Typer(
    help="Ask questions about a local Git repository.",
    no_args_is_help=False,
)


def _prompt_for_repository_path() -> Path:
    while True:
        raw_path = typer.prompt("Enter the local git repository path")
        repo_path = Path(raw_path).expanduser().resolve()

        if not repo_path.exists() or not repo_path.is_dir():
            typer.echo("That path does not exist or is not a directory.")
            continue

        if not (repo_path / ".git").exists():
            typer.echo("That directory does not look like a git repository.")
            continue

        return repo_path


def _prompt_yes_no(message: str) -> bool:
    while True:
        answer = typer.prompt(message).strip().lower()
        if answer == "y":
            return True
        if answer == "n":
            return False

        typer.echo("Please enter 'y' for yes or 'n' for no.")


def _prompt_for_question() -> str:
    while True:
        question = typer.prompt("Ask a question about this repository").strip()
        if question:
            return question

        typer.echo("Please enter a non-empty question.")


def _index_repository(repo_path: Path) -> None:
    from repo_chat.indexer.indexing import index_repository

    typer.echo("Indexing...")
    result = index_repository(repo_path)

    if result.skipped_existing_index:
        should_reindex = _prompt_yes_no(
            f"Existing index found for '{result.collection_name}' "
            f"with {result.chunks_seen} chunks. Re-index? [y/n]"
        )
        if not should_reindex:
            typer.echo(f"Using existing Chroma collection '{result.collection_name}'.")
            return

        typer.echo("Deleting existing index and re-indexing...")
        result = index_repository(repo_path, reindex=True)

    typer.echo(
        f"Indexed {result.chunks_indexed} chunks from {result.files_seen} files "
        f"into Chroma collection '{result.collection_name}'."
    )


def _resolve_question(repo_path: Path, question: str) -> None:
    from repo_chat.resolver.resolver import resolve_question

    typer.echo("Searching relevant chunks...")
    result = resolve_question(repo_path=repo_path, question=question)

    if not result.chunks:
        typer.echo("No relevant chunks found.")
        return

    typer.echo("Relevant chunks:")
    for index, chunk in enumerate(result.chunks, start=1):
        typer.echo(
            f"{index}. {chunk.file}:{chunk.start_line}-{chunk.end_line} "
            f"({chunk.language.value}, distance={chunk.distance:.4f})"
        )


@app.command("delete-index")
def delete_index(
    repo_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the local repository whose index should be deleted.",
    ),
) -> None:
    """Delete an existing local vector index for a repository."""
    from repo_chat.indexer.indexing import delete_repository_index

    result = delete_repository_index(repo_path)
    if not result.deleted:
        typer.echo(f"No Chroma collection found for '{result.collection_name}'.")
        return

    typer.echo(f"Deleted Chroma collection '{result.collection_name}'.")


@app.callback(invoke_without_command=True)
def start(ctx: typer.Context) -> None:
    """Start the interactive repository chat flow."""
    if ctx.invoked_subcommand is not None:
        return

    typer.echo("Welcome to Repo Chat.")
    typer.echo("Let's start by choosing a local git repository to inspect.")

    repo_path = _prompt_for_repository_path()
    typer.echo(f"Repository selected: {repo_path}")
    _index_repository(repo_path)
    question = _prompt_for_question()
    _resolve_question(repo_path, question)


def main() -> None:
    """Application startup entry point."""
    app()


if __name__ == "__main__":
    main()
