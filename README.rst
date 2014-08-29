====
Doc8
====

Doc8 is a *opinionated* style checker for sphinx (or other) `rst`_
documentation.

Features
--------

* Ability to parse and validate rst files.

QuickStart
==========

::

    pip install doc8

To run doc8 just invoke it against any doc directory::

    $ doc8 coolproject/docs

Usage
=====

Command line usage
******************

::

    $ doc8  -h

    usage: doc8 [-h] [--config path] [--allow-long-titles] [--ignore code]
                [--no-sphinx] [--ignore-path path] [--max-line-length int]
                [-e extension] [-v]
                [path [path ...]]

    Check documentation for simple style requirements.

    What is checked:
        - invalid rst format - D000
        - lines should not be longer than 79 characters - D001
          - exception: line with no whitespace except in the beginning
          - exception: lines with http or https urls
          - exception: literal blocks
          - exception: rst target directives
        - no trailing whitespace - D002
        - no tabulation for indentation - D003
        - no carriage returns (use unix newlines) - D004

    positional arguments:
      path                  path to scan for doc files (default: os.getcwd())

    optional arguments:
      -h, --help            show this help message and exit
      --config path         user config file location (default: doc8.ini, tox.ini,
                            pep8.ini, setup.cfg)
      --allow-long-titles   allow long section titles (default: False)
      --ignore code         ignore the given errors code/codes
      --no-sphinx           do not ignore sphinx specific false positives
      --ignore-path path    ignore the given directory or file (globs are
                            supported)
      --max-line-length int
                            maximum allowed line length (default: 79)
      -e extension, --extension extension
                            check file extensions of the given type (default:
                            .rst, .txt)
      -v, --verbose         run in verbose mode

Ini file usage
**************

Instead of using the CLI for options the following files will also be examined
for ``[doc8]`` sections that can also provided the same set of options. If
the ``--config path`` option is used these files will not be examined for in
the current working directory and that configuration path will be used
instead.

* ``$CWD/doc8.ini``
* ``$CWD/tox.ini``
* ``$CWD/pep8.ini``
* ``$CWD/setup.cfg``

An example section that can be placed into one of these files::

    [doc8]

    ignore_paths=/tmp/stuff,/tmp/other_stuff
    max_line_length=99
    verbose=1

.. _rst: http://docutils.sourceforge.net/docs/ref/rst/introduction.html
