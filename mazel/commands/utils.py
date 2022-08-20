import click

from mazel.workspace import Workspace


def current_workspace() -> Workspace:
    """Throw exception if not currently in a workspace"""
    workspace = Workspace.find()

    if workspace is None:
        raise click.ClickException("Not in a workspace")

    return workspace
