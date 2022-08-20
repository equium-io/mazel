import shutil
from pathlib import Path
from typing import Any, Dict, Optional

import click
import tomlkit

from mazel.commands.utils import current_workspace
from mazel.exceptions import InvalidPackage, MazelException
from mazel.workspace import Workspace

FrontMatter = Dict[str, Any]


class InvalidReadme(MazelException):
    ...


def get_root(workspace: Workspace) -> Path:
    return workspace.path.joinpath("docs/team.equium.io/content/packages")


@click.command()
def link_readme() -> None:
    """Copy the README.md for each package into team.equium.io"""
    workspace = current_workspace()
    root = get_root(workspace)

    # Clean out the path so no leftovers exist
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(exist_ok=True, parents=True)

    # README.md in project's root
    copy_readme(
        workspace.path.joinpath("README.md"),
        root,
        front_matter={"title": "READMEs", "menu": {"main": {"weight": 30}}},
    )

    # Mimic directory structure, copying README's for each package.
    # Generate a blank entry for any intermediate directories so hugo will insert list
    for package in workspace.packages():
        if not package.path_exists("README.md"):
            raise InvalidPackage(f"{package.label_path} lacks a README.md")

        # Recreate the packages' folder structure into the docs' content directory
        outdir = root.joinpath(package.path.relative_to(workspace.path))
        outdir.mkdir(parents=True, exist_ok=True)
        copy_readme(package.path.joinpath("README.md"), outdir)

        # Create any intermediate directories from the package to the workspace root.
        # relative_to is an extra sanity check -- will throw ValueError if we've gone
        # outside the root
        curdir = package.path.relative_to(workspace.path).parent
        while curdir.resolve() != workspace.path and curdir.resolve().relative_to(
            workspace.path
        ):
            outdir = root.joinpath(curdir)
            index = outdir.joinpath("_index.md")
            # TODO Consider avoiding re-writing the index (will get reprocessed for
            # every package). But need to clean the outdir
            if not index.exists():
                outdir = root.joinpath(curdir)
                readme = curdir.joinpath("README.md")
                if readme.exists():
                    # if a intermediate directory has a README.md, then use that
                    copy_readme(readme, outdir)
                else:
                    # Otherwise, create an empty _index.md, so that that hugo will
                    # generate the directory listings
                    write_index(index, "")

            curdir = curdir.parent


def copy_readme(
    readme: Path, outdir: Path, front_matter: Optional[FrontMatter] = None
) -> None:
    if front_matter is None:
        front_matter = {}

    if not readme.exists():
        return

    # Rename from README to _index to allow serving
    index = outdir.joinpath("_index.md")
    with readme.open() as f:
        try:
            data = list(f.readlines())
            # Turn the first line (which should be the <h1> into a description,
            # since the hugo template uses `title` as the h1
            description = data.pop(0).lstrip("#").strip()
        except Exception as e:
            raise InvalidReadme(f"Error processing {readme}: {e}")

        # TODO Consider incorporating data from BUILD.toml into the produced
        # file, e.g. dependencies, runtimes
        # TODO GitHub link to README.md
        content = "".join(data)

        front_matter.update({"description": description})

        write_index(index, content=content, front_matter=front_matter)


def write_index(
    path: Path, content: str, front_matter: Optional[FrontMatter] = None
) -> None:
    if front_matter is None:
        front_matter = {}

    front_matter.setdefault("title", path.parent.name)
    front_matter_content = f"+++\n{tomlkit.dumps(front_matter)}\n+++\n"

    with path.open("w") as f:
        f.write(front_matter_content)
        f.write(content)

    click.echo(path.relative_to(Path.cwd()))
