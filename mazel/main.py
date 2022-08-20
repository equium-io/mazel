import click

from .commands.clean import clean
from .commands.contrib import contrib
from .commands.echo import echo
from .commands.format import format
from .commands.info import info
from .commands.run import run
from .commands.test import test


@click.group()
def cli() -> click.Group:
    pass


cli.add_command(test)
cli.add_command(run)
cli.add_command(info)
cli.add_command(echo)
# TODO cli.add_command(build)

# Plugins that may not be generalizable
cli.add_command(contrib)

# WARN: not bazel commands, perhaps specific rules?
#   like `run //*:clean?` or `plugin clean`?
cli.add_command(clean)
cli.add_command(format)


if __name__ == "__main__":
    cli()
