"""
Contrib commands are things that are not part of bazel and likely may not be
applicable if mazel were generalized to other projects.

Longer-term, using a plugin-based approach with dynamic registration may be ideal
"""
import click

# TODO dynamic registration of contrib commands
from mazel.contrib.dependabot import dependabot
from mazel.contrib.link_readme import link_readme


@click.group()
def contrib() -> click.Group:
    pass


contrib.add_command(dependabot)
contrib.add_command(link_readme)
