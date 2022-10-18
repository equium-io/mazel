``mazel`` Subcommands
=====================

.. _commands-run:

``run``
-------

::


   Usage: mazel run [OPTIONS] [LABEL]

     Runs a specific Makefile target.

     The equivalent of `cd mypackage; make shell`:

        mazel run //mypackage:shell

   Options:
     --with-ancestors
     --with-descendants
     --modified-since TEXT  Only run for packages with modified files according
                            to git. Takes in a commit like object, e.g. 39fc076
                            or a range 39fc076..6ff72ca. End commit defaults to
                            HEAD
     --help                 Show this message and exit.

.. _commands-test:

``test``
--------

::

   Usage: mazel test [OPTIONS] [LABEL]

   Options:
     --test_output [streamed|errors]
                                     Only show stdout/stderr after error, or
                                     stream everything.
     --with-ancestors
     --with-descendants
     --modified-since TEXT           Only run for packages with modified files
                                     according to git. Takes in a commit like
                                     object, e.g. 39fc076 or a range
                                     39fc076..6ff72ca. End commit defaults to
                                     HEAD
     --help                          Show this message and exit.


.. _selective-builds:

Selective Builds for Modified Packages
--------------------------------------

Using the ``--modified-since=<COMMIT>`` option, we can run only packages that contain files that have been added/removed/changed since the ``COMMIT``.  Typically ``COMMIT`` will be the last succesful CI run or the branch point off the ``main`` branch. When we also add  ``--with-descendants``, we can also run with any packages that depend upon our changed package(s).

So if :file:`//libs/py/common/libcommon.py` changed, and :file:`//services/backend` uses :file:`//libs/py/common`::

  # Would run the test target on //libs/py/common
  mazel test --modified-since=abcd1234 //

  # Would run the test target on //libs/py/common and //services/backend
  mazel test --modified-since=abcd1234 --with-descendants //

Suggested zsh / bash Aliases
----------------------------

In your :file:`~/.zshrc` or :file:`~/.bashrc` consider adding aliases for quicker access to these subcommands::

  alias mt="mazel test"
  alias mr="mazel run"


For example::

   mr //:format
   mt //
