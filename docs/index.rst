``mazel``: make helpers for monorepos
=====================================

> bazel(-ish) for Makefiles = **mazel**

``mazel`` is a simple `bazel <https://bazel.build/>`_ -inspired `Make <https://www.gnu.org/software/make/>`_-based build system for monorepos.

The goal is to not create another build system, rather we provide simple helpers around GNU `make`, along with common (though not required) Makefile patterns and the ability to process language-specific dependency files (:file:`pyproject.toml`, :file:`package.json`)

mazel provides:

1. Ability to execute make targets in one more :ref:`Packages <concepts-package>` via a :ref:`Label syntax <concepts-label>`
2. Dependency graph to allow execution of targets in a logical order. Either explicitly specificied or automatically parsed from :doc:`Supported Runtime <runtimes>` including poetry and npm.
3. Ability to only run for a subset of modified packages according the the dependency graph. :ref:`Selective Builds <selective-builds>`


Run the ``clean`` target in all packages in a monorepo (``//`` indicates :ref:`Workspace <concepts-workspace>` root)::

  mazel run //:clean



`mazel run` typically requires the `:target` specifier.  However some commands automatically default to a target (e.g. `:test` for `mazel test`)::

   # Test one package
   mazel test //libs/common
   # Or test multiple packages
   mazel test //


With :ref:`Selective Builds <selective-builds>`, only modified packages (and optionally downstream packages) can be run::

  mazel test --modified-since=abcd1234 --with-descendants //


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   why
   concepts
   commands
   build-toml
   runtimes
   make/index
   contribute
   changelog
