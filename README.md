# mazel: make helpers for monorepos

>  bazel(-ish) for Makefiles = **mazel**

`mazel` is a simple [bazel](https://bazel.build/)-inspired Makefile-based build system for monorepos.

The goal is to not create another build system, rather we provide simple helpers around GNU `make`, along with common (though not required) Makefile patterns.

mazel provides:
1. Ability to execute make targets in one or more subpaths. See [mazel labels](#mazel-labels)
2. Dependency graph to allow execution of targets in a logical order. Either parsed from the package manager (e.g. poetry's `pyproject.toml` or npm's `package.json`).

## mazel concepts

Following [bazel's concepts](https://docs.bazel.build/versions/master/build-ref.html)

* **Workspace**: The root of the monorepo. Contains a `WORKSPACE.toml` file
* **Package**: A specific service, library, tool, etc. If we used a multi-repo approach, these would likely align to individual projects / repositories. Contains a `BUILD.toml` file, which specifies the runtime

Under the hood, we utilize well-designed Makefiles that call out to language-specific dependency and packaging tools, e.g. [poetry](https://python-poetry.org/) for Python, docker, npm, etc.

## mazel labels

In the spirit of [bazel's labels](https://docs.bazel.build/versions/master/build-ref.html#labels), we can specify packages and targets using a `//dir/package:target` syntax.  The ``//`` specifies the Workspace root, `dir/package` is the path to the package, and `:target` indicates the target in the Makefile to execute.  The syntax also supports relative paths and partial paths.


```
//dir/package:target   # Full label
dir/package:target     # Relative path label
package:target         # Relative path label, if current directory is `dir`
:target                # Target-only label, useful if inside `dir/package`
//dir:target           # Partial path label, that would run `:target` in all packages under `dir`
```

`mazel run` typically requires the `:target` specifier.  However some commands automatically default to a target (e.g. `:test` for `mazel test`).

Examples:

```
mazel test //libs/py/common          # Runs `make test` for the common library
mazel test                           # Runs tests for any packages under the current directory
mazel format //libs/py               # Code formats all code under libs/py
mazel run //tools/docker/base:image  # Builds the equium/base docker image
```

This label syntax is designed to make it quick to run actions in the current package, while simple enough to run actions for other packages in the repo.
