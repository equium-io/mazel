Runtimes
========

.. note::

   :doc:`Pull Requests </contribute>` for additional runtimes are welcome. If your runtime is not present yet, :ref:`build_toml-depends_on` still allows for explicit specification of dependencies.


Runtimes provide language-specific package manager wrappers for parsing out Workspace-relative package dependencies.

Python (poetry)
---------------

Parses the :file:`pyproject.toml` for the ``[tool.poetry.dependencies]`` and ``[tool.poetry.dev-dependencies]`` sections.

Looks for `path dependencies <https://python-poetry.org/docs/dependency-specification/#path-dependencies>`_::

   [tool.poetry.dependencies]
   python = "~3.10"
   "sampleproject.common" = {path = "../../libs/py/common", develop = true}


Javascript (npm)
----------------
Parses the :file:`package.json` for the ``dependencies`` and ``devDependencies``.

Looks for `local paths <https://docs.npmjs.com/cli/v6/configuring-npm/package-json#local-paths>`_::

   "dependencies": {
     "@sampleproject/common": "file:../../libs/js/common",
   }
