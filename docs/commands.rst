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
     --help              Show this message and exit.

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
     --help                          Show this message and exit.

Suggested zsh / bash Aliases
----------------------------

In your :file:`~/.zshrc` or :file:`~/.bashrc` consider adding aliases for quicker access to these subcommands::

  alias mt="mazel test"
  alias mr="mazel run"


For example::

   mr //:format
   mt //
