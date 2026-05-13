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


def _index_repository(repo_path: Path) -> None:
    from repo_chat.indexer.indexing import index_repository

    typer.echo("Indexing...")
    result = index_repository(repo_path)

    if result.skipped_existing_index:
        typer.echo(
            f"Using existing Chroma collection '{result.collection_name}' "
            f"with {result.chunks_seen} chunks."
        )
        return

    typer.echo(
        f"Indexed {result.chunks_indexed} chunks from {result.files_seen} files "
        f"into Chroma collection '{result.collection_name}'."
    )


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


@app.command()
def ask(
    repo_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Path to the local repository to inspect.",
    ),
    question: str = typer.Argument(..., help="Question to ask about the codebase."),
) -> None:
    """Ask a question about a local repository."""
    typer.echo(f"Repository: {repo_path}")
    typer.echo(f"Question: {question}")
    _index_repository(repo_path)
    typer.echo("Retrieval and answer generation will be implemented next.")


def main() -> None:
    """Application startup entry point."""
    app()


if __name__ == "__main__":
    main()
