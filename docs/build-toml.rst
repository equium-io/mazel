:file:`BUILD.toml`
==================

The :file:`BUILD.toml` sits in the root of a :ref:`concepts-package` and helps us define the dependency graph of the :ref:`concepts-workspace`.

The minimal :file:`BUILD.toml` simply uses the ``[package]`` header::

  [package]


Dependencies
------------


:file:`BUILD.toml` has two optional keys that allow defining the dependency, :ref:`build_toml-depends_on` and :ref:`build_toml-runtimes`.

.. _build_toml-depends_on:

``depends_on``
~~~~~~~~~~~~~~

``depends_on`` allows specifying the path to any packages this package requires.  It is generic and language-agnostic.  

In our :ref:`sample-monorepo-layout`, ``//services/backend`` depends upon ``//libs/py/common``, we can specify this by::

  [package]
  depends_on = [
      "//libs/py/common",
  ]


.. _build_toml-runtimes:

``runtimes``
~~~~~~~~~~~~~~

However, we often will also be specify relative dependencies in the language-specific package management files (:file:`pyproject.toml`, :file:`packages.json`, etc).  In this case, the ``depends_on`` is duplicating, so we can use a :doc:`Supported Runtime <runtimes>` to parse the dependency file and dynamically create the dependencies

If our :file:`//services/backend/pyproject.toml` has a relative dependency to ``//libs/py/common``::

  [tool.poetry.dependencies]
   python = "~3.10"
   "sampleproject.common" = {path = "../../libs/py/common", develop = true}


The :file:`BUILD.toml` can skip the ``depends_on`` and just define a ``runtimes``::

  [package]
  runtimes = ["python"]


``runtimes`` and ``depends_on`` can be mixed together, expecially if there is not yet a :doc:`Supported Runtime <runtimes>`.

