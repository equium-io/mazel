Makefile Best Practices
========================


Much of Equium's Makefiles were inspired by Davis Hansson's `"Your Makefiles are wrong" <https://tech.davis-hansson.com/p/make/>`_ -- **give it a read**!

See :doc:`opinionated` for detailed examples


.. _best-practices-consistent-targets:

Consistent Targets
------------------

mazel largely works by having consistent targets across Makefiles.  Use common targets like ``test``, ``format``, and ``lint``



**BAD**

:file:`js-package/Makefile`::

  eslint:
  > eslint --fix .
  .PHONY: eslint

:file:`py-package/Makefile`::

  black:
  > black .
  .PHONY: black


**BETTER**

:file:`js-package/Makefile`::

  format:
  > eslint --fix .
  .PHONY: eslint

:file:`py-package/Makefile`::

  format:
  > black .
  .PHONY: format

Now the command ``mazel run //:format`` will work against both packages.


See :ref:`Makefile Mixins <opinionated-mixins>` for how we can combine if there are multiple rules that should all contribute to the same target.

