from pathlib import Path

import typer


app = typer.Typer(
    help="Ask questions about a local Git repository.",
    no_args_is_help=True,
)


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
    typer.echo("Indexing and retrieval will be implemented next.")


def main() -> None:
    """Application startup entry point."""
    app()


if __name__ == "__main__":
    main()
