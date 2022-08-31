# mazel: make helpers for monorepos

>  bazel(-ish) for Makefiles = **mazel**

`mazel` is a simple [bazel](https://bazel.build/)-inspired Makefile-based build system for monorepos.

The goal is to not create another build system, rather we provide simple helpers around GNU `make`, along with common (though not required) Makefile patterns.

mazel provides:
1. Ability to execute make targets in one or more subpaths.
2. Dependency graph to allow execution of targets in a logical order. Either parsed from the package manager (e.g. poetry's `pyproject.toml` or npm's `package.json`).


```
mazel test //libs/py/common          # Runs `make test` for the common library
mazel test                           # Runs tests for any packages under the current directory
mazel format //libs/py               # Code formats all code under libs/py
mazel run //tools/docker/base:image  # Builds the base docker image
```

See https://mazel.readthedocs.io/ for more info
