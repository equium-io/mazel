Contributing
============

https://github.com/equium-io/mazel

Wish list
---------

* Additional :doc:`runtimes`
  

Environment
-----------

Development of mazel currently requires make >= 4.0 and `poetry <https://python-poetry.org/>`_.

mazel can be used with older make, but in the project's `Makefile <https://github.com/equium-io/mazel/blob/main/Makefile>`_, we utilize ``.RECIPEPREFIX`` (this could be removed in the future).

On MacOS, this will require installing GNU Make via homebrew::

  brew install make

You will likely need to add ``$HOMEBREW_PREFIX/opt/make/libexec/gnubin`` onto your path ``$PATH``, so that :command:`which make` returns GNU Make, not the MacOS builtin BSD Make 3.81.


Testing
-------

To run the test suite::

   make test


Note that mazel can be self-hosting, so the same command can be run via::

  poetry run mazel test //

Before submitting a Pull Request, please ensure that the the code is formatted, type definitions are accurate, and there are no lint issues::

  make format
  make mypy
  make lint


Documentation
-------------

To compile the sphinx documentation run the liveserver::

  make docs-serve

Alternatively, the documentation can be compiled via::

  make docs
