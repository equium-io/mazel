mazel Concepts
===============

Following `bazel's concepts <https://bazel.build/concepts/build-ref>`_:

.. _concepts-workspace:

Workspace
----------

The "Workspace" is the root of the monorepo.

Contains a :file:`WORKSPACE.toml` file, which is currently empty.  Contains one or more :ref:`Packages <concepts-package>`.

.. _concepts-package:

Package
-------

"Packages" are subdirectories that contain a specific service, library, tool, etc.

If we used a multi-repo approach, these would likely align to individual projects / repositories. Contains a :doc:`build-toml` file, which specifies the runtime as well as a Makefile.

Under the hood, we utilize well-designed Makefiles that call out to language-specific dependency and packaging tools (see :doc:`runtimes`).

.. _sample-monorepo-layout:

Sample Monorepo Structure
~~~~~~~~~~~~~~~~~~~~~~~~~

A typical monorepo may have the following structure splitting libraries and services::

  WORKSPACE.toml
  libs/
    js/
      common/
        BUILD.toml
        package.json
    py/
      common/
        BUILD.toml
        pyproject.toml
  services/
    frontend/
      BUILD.toml
      package.json
    backend/
      BUILD.toml
      pyproject.toml
  tools/
     deployer/
       BUILD.toml
       go.mod
     docker/
       python/
         BUILD.toml

In this example, there are 4 "Packages": ``//libs/common``, ``//services/frontend``, ``//services/backend``, ``//tools/deployer``


.. _concepts-target:

Target
-------

A "Target" refers to a `Makefile rule <https://www.gnu.org/software/make/manual/html_node/Rules.html#Rules>`_ to execute.

For example if our :file:`Makefile` has a ``format`` rule::

  format:
      black .
  .PHONY: format


If we are inside the package (at the package's root or a subdirectory), we can execute the this target via :command:`mazel run :format`.  This effectively is the same as running :command:`make format`, but becomes more powerful when we can run this make command from any path in our Workspace.


See :doc:`/make/best-practices` to ensure consistent workspace-wide target names.

.. _concepts-label:

Labels
------

In the spirit of `bazel's labels <https://bazel.build/concepts/build-ref#labels>`_, we can specify packages and targets using a ``//dir/package:target`` syntax.

The ``//`` specifies the Workspace root, ``dir/package`` is the path to the package, and ``:target`` indicates the target in the Makefile to execute.  The syntax also supports relative paths and partial paths.


::

   //dir/package:target   # Full label
   dir/package:target     # Relative path label
   package:target         # Relative path label, if current
                          #   directory is `dir`
   :target                # Target-only label, useful if
                          #   inside `dir/package`
   //dir:target           # Partial path label, that would run
                          #   `:target` in all packages under `dir`

:command:`mazel run` typically requires the ``:target`` specifier.  However some commands automatically default to a target (e.g. `:test` for `mazel test`).

Examples::

  mazel test //libs/py/common          # Runs `make test` for the common library
  mazel test                           # Runs tests for any packages under the current directory
  mazel format //libs/py               # Code formats all code under libs/py
  mazel run //tools/docker/base:image  # Builds the base docker image

This label syntax is designed to make it quick to run actions in the current package, while simple enough to run actions for other packages in the repo.
