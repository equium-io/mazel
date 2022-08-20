import operator
from copy import deepcopy
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List

import click
from ruamel.yaml import YAML

from mazel.commands.utils import current_workspace
from mazel.workspace import Workspace

# https://docs.github.com/en/code-security/supply-chain-security\
#    /configuration-options-for-dependency-updates#package-ecosystem
# Map between runtime_label and package-ecosystem
PACKAGE_ECOSYSTEM = {
    "python": "pip",
    # Temporarily disabling docker dependabot as once we switched to using us.gcr.io
    #  dependabot could not authenticate. Open to revisiting. Refs #1482 & #1459
    "docker": None,  # "docker",
    "javascript": "npm",
    "meteor": "npm",
    "go": "gomod",
}
PACKAGE_DEFAULTS = {
    "open-pull-requests-limit": 10,
    "schedule": {
        "interval": "monthly",
    },
    "ignore": [
        {
            # Reduce some noise, as we are not keeping up. Wait for minor version bumps
            "dependency-name": "*",
            "update-types": ["version-update:semver-patch"],
        }
    ],
}
CONFIG_FILE = ".github/dependabot.yml"


@click.command()
@click.option("--check", is_flag=True)
def dependabot(check: bool = False) -> None:
    """Generate the .github/dependabot.yml file"""
    # https://docs.github.com/en/code-security/supply-chain-security\
    #    /configuration-options-for-dependency-updates
    workspace = current_workspace()

    config_path = get_config_path(workspace)

    new_config = make_config(workspace)
    existing_config = read_config_yml(config_path)

    if new_config == existing_config:
        click.echo(f"{CONFIG_FILE} is current")
    elif check:
        raise click.ClickException(
            f"{CONFIG_FILE} is out of date. Run `mazel contrib dependabot`"
        )
    else:
        write_config_yml(config_path, new_config)
        click.echo(f"{CONFIG_FILE} updated")


def get_config_path(workspace: Workspace) -> Path:
    return workspace.path.joinpath(CONFIG_FILE)


def read_config_yml(path: Path) -> str:
    with open(path, "r") as f:
        return f.read()


def write_config_yml(path: Path, data: str) -> None:
    with open(path, "w") as f:
        f.write(data)


def make_config(workspace: Workspace) -> str:
    output = StringIO()
    output.write("# Do not edit manually, regenerate with `mazel contrib dependabot`\n")

    data = {
        "version": 2,
        "updates": updates(workspace),
    }
    YAML().dump(data, output)

    return output.getvalue()


def updates(workspace: Workspace) -> List[Dict[str, Any]]:
    entries = []
    for package in workspace.packages():
        for runtime in package.runtimes():

            package_ecosystem = PACKAGE_ECOSYSTEM[runtime.runtime_label]
            if package_ecosystem is None:
                # Runtime is disabled for dependabot checking
                continue

            path = package.path.relative_to(workspace.path)

            # TODO Consider allowing customization and additional options in BUILD.toml,
            # including version ignore & open-pull-requests-limit
            options = {
                "package-ecosystem": package_ecosystem,
                "directory": f"/{path}",
            }
            # prevent using yaml aliases via deepcopy
            options.update(deepcopy(PACKAGE_DEFAULTS))

            entries.append(options)

    # Ensure consistent ordering
    return sorted(entries, key=operator.itemgetter("directory", "package-ecosystem"))
