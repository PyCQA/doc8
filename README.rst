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

    $ ./doc8  -h
    usage: doc8 [-h] [--config path] [--allow-long-titles] [--ignore code]
                [path [path ...]]

    Check documentation for simple style requirements.

    What is checked:
        - lines should not be longer than 79 characters - D001
          - exception: line with no whitespace except in the beginning
          - exception: lines with http or https urls
          - exception: literal blocks
          - exception: rst target directives
        - no trailing whitespace - D002
        - no tabulation for indentation - D003
        - no carriage returns (use unix newlines) - D004

    positional arguments:
      path                 path to scan for *.rst, *.txt files (default:
                           os.getcwd())

    optional arguments:
      -h, --help           show this help message and exit
      --config path        user config file location (default: doc8.ini, tox.ini,
                           pep8.ini, setup.cfg)
      --allow-long-titles  allow long section titles (default: False)
      --ignore code        ignore the given errors code/codes
      --max-line-length int
                           maximum allowed line length (default: 79)

.. _rst: http://docutils.sourceforge.net/docs/ref/rst/introduction.html
