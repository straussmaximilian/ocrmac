"""Console script for ocrmac."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for ocrmac."""

    click.echo(
        "No CMD tool implemented yet. Consider creating an issue or a pull request if this would be useful for you."
    )

    if False:
        click.echo("Replace this message by putting your code into " "ocrmac.cli.main")
        click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
