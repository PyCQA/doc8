====
Doc8
====

Doc8 is a *opinionated* style checker for sphinx (or other) `rst`_
documentation.

QuickStart
==========

::

    pip install doc8

To run doc8 just invoke it against any doc directory::

    $ doc8 coolproject/docs

Usage
=====

::

    $ doc8 -h
    usage: doc8 [-h] [path [path ...]]

    Check documentation for simple style requirements.

    What is checked:
        - lines should not be longer than 79 characters - D001
          - exception: line with no whitespace except maybe in the beginning
          - exception: line that starts with '..' -- longer directives are allowed,
            including footnotes
        - no trailing whitespace - D002
        - no tabulation for indentation - D003
        - no carriage returns (use unix newlines) - D004

    positional arguments:
      path        path to scan for *.rst, *.txt files (default: os.getcwd())

    optional arguments:
      -h, --help  show this help message and exit

.. _rst: http://docutils.sourceforge.net/docs/ref/rst/introduction.html
