Why Another Build System?
=========================

We don't think of mazel as a build system, but rather an enhancement to allow using the extremely powerful GNU Make to work more effectively in monorepos.

We had two problems using Make alone:

1. Ability to compute cross-package dependencies and ensure upstream and/or downstream packages are built.
2. Ability to run :command:`make` easily against other packages in the workspace or from subdirectories of the package.


Our first attempt was to use `bazel <https://bazel.build/>`_ for our monorepo.  bazel is an incredibly powerful tool, but in order take advantage of it, we ran into several problems (in 2020):

* Requires tossing out standard packaging tools, replaced by bazel's specific ``rules_*``.  We ran into issues on MacOS cross compiling with rules_python and rules_docker
* Requires a dedicated team to manage.

Our goal was to create a tool that would be easy to someday migrate into bazel (so the :ref:`mazel Labels <concepts-label>` and command options are heavily inspired by bazel).

Alternatives
------------

* `bazel <https://bazel.build/>`_
* `pants <https://www.pantsbuild.org/>`_
* `Nx <https://nx.dev/>`_
* `lerna <https://lerna.js.org/>`_ - Javascript only
* `Turborepo <https://turborepo.org/>`_ - Javascript only
* `Make <https://www.gnu.org/software/make/>`_
* `Meson <https://mesonbuild.com/>`_
