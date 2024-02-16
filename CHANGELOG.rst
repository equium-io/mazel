Changelog
=========

0.0.5 - 2024-02-16
------------------

- Open Python version specificer to allow Python 3.11+


0.0.4 - 2022-11-10
------------------

- Avoid including "sibling" or "cousin" packages of the start node when using both ``--with-descendants`` and ``--with-ancestors``.  Only descendants of the start node and direct ancestors of the start node are including, not descendants of any parent / grandparent node.


0.0.3 - 2022-10-16
------------------

- Added ``--modified-since`` to support :ref:`Selective Builds <selective-builds>`


0.0.2 - 2022-08-22
------------------

- Initial public release
