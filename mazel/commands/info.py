from typing import Any

import click

from .utils import current_workspace


@click.command()
@click.argument("fact", required=False)
# @click.option("--cwd", default=None, help="", type=click.Path(file_okay=False))
def info(fact: str = None) -> None:
    """Facts about the Workspace. Can request a specific FACT or receive all."""

    # cwd=Path(cwd) if cwd else None
    info = current_workspace().info()

    if fact is not None:
        # Single Fact
        try:
            fact = info.get_fact(fact)
        except AttributeError:
            raise click.ClickException(f"{fact} not a valid FACT")

        click.echo(format_fact(fact))
    else:
        # All Facts
        facts = info.collect()
        for name, fact in facts.items():
            click.echo(name + ": " + click.style(format_fact(fact), fg="blue"))


def format_fact(fact: Any) -> str:
    if fact is None:
        return ""
    if isinstance(fact, list):
        return ", ".join(fact)
    return str(fact)
