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
        question = typer.prompt("Ask a question about this repository, or type 'exit'").strip()
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

    typer.echo("Searching and generating an answer...")
    result = resolve_question(repo_path=repo_path, question=question)

    typer.echo("")
    typer.echo(result.answer)


def _questions_loop(repo_path: Path) -> None:
    while True:
        question = _prompt_for_question()
        if question.lower() == "exit":
            typer.echo("Goodbye.")
            return

        _resolve_question(repo_path, question)
        typer.echo("")


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
    _questions_loop(repo_path)


def main() -> None:
    """Application startup entry point."""
    app()


if __name__ == "__main__":
    main()
