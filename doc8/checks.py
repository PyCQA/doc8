# Copyright (C) 2014 Ivan Melnikov <iv at altlinux dot org>
#
# Author: Joshua Harlow <harlowja@yahoo-inc.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import abc
import collections
import re

from docutils import nodes as docutils_nodes
import six

from doc8 import utils


# Most of the known directives can be mapped to specific types here,
# so that we can examine them...
#
# See: http://docutils.sourceforge.net/docs/ref/rst/directives.html
_RST_DIRECTIVES = tuple([
    docutils_nodes.admonition,
    docutils_nodes.attention,
    docutils_nodes.caution,
    docutils_nodes.compound,
    docutils_nodes.container,
    docutils_nodes.danger,
    docutils_nodes.error,
    docutils_nodes.figure,
    docutils_nodes.footer,
    docutils_nodes.header,
    docutils_nodes.hint,
    docutils_nodes.image,
    docutils_nodes.important,
    docutils_nodes.inline,
    docutils_nodes.math,
    docutils_nodes.note,
    docutils_nodes.raw,
    docutils_nodes.rubric,
    docutils_nodes.sidebar,
    docutils_nodes.table,
    docutils_nodes.tip,
    docutils_nodes.topic,
    docutils_nodes.warning,
])
_RST_DIRECTIVES_MAPPING = {}
for directive_cls in _RST_DIRECTIVES:
    directive_name = directive_cls.__name__.split(".")[-1]
    _RST_DIRECTIVES_MAPPING[directive_name] = directive_cls

_RST_DIRECTIVES_EXTRA = frozenset([
    # Built-in rst directives not listed above (as they are not mapped
    # to types, for some reason).
    'code-block',
    'code',
    'contents',
    'csv-table',
    'epigraph',
    'glossary',
    'highlights',
    'include',
    'line-block',
    'meta',
    'parsed-literal',
    'section-numbering',
    'sectnum',
    'target-notes',
])

_SPHINX_RST_DIRECTIVES = frozenset([
    # These are common sphinx directives additions...
    # See: http://sphinx-doc.org/markup/para.html
    'centered',
    'deprecated',
    'function',
    'hlist',
    'productionlist',
    'seealso',
    'toctree',
    'versionadded',
    'versionchanged',

    # See: http://sphinx-doc.org/domains.html
    'py:attribute',
    'py:class',
    'py:classmethod',
    'py:currentmodule',
    'py:data',
    'py:decorator',
    'py:decoratormethod',
    'py:exception',
    'py:function',
    'py:method',
    'py:module',

    'c:function',
    'c:member',
    'c:macro',
    'c:type',
    'c:var',

    'cpp:class',
    'cpp:function',
    'cpp:member',
    'cpp:var',
    'cpp:type',
    'cpp:type',
    'cpp:enum',
    'cpp:enum-struct',
    'cpp:enum-class',
    'cpp:enumerator',
    'cpp:namespace',

    'option',
    'envvar',
    'program',
    'describe',
    'object',

    'js:function',
    'js:class',
    'js:data',
    'js:attribute',

    'rst:role',
    'rst:directive',

    # See: http://sphinx-doc.org/markup/misc.html
    'codeauthor',
    'index',
    'only',
    'sectionauthor',
    'tabularcolumns',
])


def _extract_node_lines(doc):
    """Extracts all the nodes and there (start, end) lines from a document."""

    def extract_lines(node, start_line):
        lines = [start_line]
        if isinstance(node, (docutils_nodes.title)):
            start = start_line - len(node.rawsource.splitlines())
            if start >= 0:
                lines.append(start)
        if isinstance(node, (docutils_nodes.literal_block)):
            end = start_line + len(node.rawsource.splitlines()) - 1
            lines.append(end)
        return lines

    def gather_lines(node):
        lines = []
        for n in node.traverse(include_self=True):
            lines.extend(extract_lines(n, find_line(n)))
        return lines

    def find_line(node):
        n = node
        while n is not None:
            if n.line is not None:
                return n.line
            n = n.parent
        return None

    def filter_systems(node):
        if utils.has_any_node_type(node, (docutils_nodes.system_message,)):
            return False
        return True

    nodes_lines = []
    first_line = -1
    for n in utils.filtered_traverse(doc, filter_systems):
        line = find_line(n)
        if line is None:
            continue
        if first_line == -1:
            first_line = line
        contained_lines = set(gather_lines(n))
        nodes_lines.append((n, (min(contained_lines),
                                max(contained_lines))))
    return (nodes_lines, first_line)


def _extract_directives(lines):
    """Extracts the raw rst directives from some content."""

    def starting_whitespace(line):
        m = re.match(r"^(\s+)(.*)$", line)
        if not m:
            return 0
        return len(m.group(1))

    def all_whitespace(line):
        return bool(re.match(r"^(\s*)$", line))

    def find_directive_end(start, lines):
        after_lines = collections.deque(lines[start + 1:])
        k = 0
        while after_lines:
            line = after_lines.popleft()
            if all_whitespace(line) or starting_whitespace(line) >= 1:
                k += 1
            else:
                break
        return start + k

    # Find where directives start & end so that we can exclude content in
    # these directive regions (the rst parser may not handle this correctly
    # for unknown directives, so we have to do it manually).
    directives = []
    directive_names = set()
    for i, line in enumerate(lines):
        directive_match = re.match(r"^\s*..\s(.*?)::\s*", line)
        if directive_match:
            directive_name = directive_match.group(1)
            if directive_name:
                directive_names.add(directive_name)
            directives.append((directive_name,
                               i, find_directive_end(i, lines)))
        elif re.match(r"^::\s*$", line):
            directives.append((None, i, find_directive_end(i, lines)))
    return directives, directive_names


@six.add_metaclass(abc.ABCMeta)
class ContentCheck(object):
    def __init__(self, cfg):
        self._cfg = cfg

    @abc.abstractmethod
    def report_iter(self, parsed_file):
        pass


@six.add_metaclass(abc.ABCMeta)
class LineCheck(object):
    def __init__(self, cfg):
        self._cfg = cfg

    @abc.abstractmethod
    def report_iter(self, line):
        pass


class CheckTrailingWhitespace(LineCheck):
    _TRAILING_WHITESPACE_REGEX = re.compile('\s$')
    REPORTS = frozenset(["D002"])

    def report_iter(self, line):
        if self._TRAILING_WHITESPACE_REGEX.search(line):
            yield ('D002', 'Trailing whitespace')


class CheckIndentationNoTab(LineCheck):
    _STARTING_WHITESPACE_REGEX = re.compile('^(\s+)')
    REPORTS = frozenset(["D003"])

    def report_iter(self, line):
        match = self._STARTING_WHITESPACE_REGEX.search(line)
        if match:
            spaces = match.group(1)
            if '\t' in spaces:
                yield ('D003', 'Tabulation used for indentation')


class CheckCarriageReturn(LineCheck):
    REPORTS = frozenset(["D004"])

    def report_iter(self, line):
        if "\r" in line:
            yield ('D004', 'Found literal carriage return')


class CheckNewlineEndOfFile(ContentCheck):
    REPORTS = frozenset(["D005"])

    def __init__(self, cfg):
        super(CheckNewlineEndOfFile, self).__init__(cfg)

    def report_iter(self, parsed_file):
        if parsed_file.lines and not parsed_file.lines[-1].endswith(b'\n'):
            yield (len(parsed_file.lines), 'D005', 'No newline at end of file')


class CheckValidity(ContentCheck):
    REPORTS = frozenset(["D000"])
    EXT_MATCHER = re.compile(r"(.*)[.]rst", re.I)

    # From docutils docs:
    #
    # Report system messages at or higher than <level>: "info" or "1",
    # "warning"/"2" (default), "error"/"3", "severe"/"4", "none"/"5"
    #
    # See: http://docutils.sourceforge.net/docs/user/config.html#report-level
    WARN_LEVELS = frozenset([2, 3, 4])

    # Only used when running in sphinx mode.
    SPHINX_IGNORES_REGEX = [
        re.compile(r'^Unknown interpreted text'),
        re.compile(r'^Unknown directive type'),
        re.compile(r'^Undefined substitution'),
        re.compile(r'^Substitution definition contains illegal element'),
    ]

    def __init__(self, cfg):
        super(CheckValidity, self).__init__(cfg)
        self._sphinx_mode = cfg.get('sphinx')

    def report_iter(self, parsed_file):
        for error in parsed_file.errors:
            if error.level not in self.WARN_LEVELS:
                continue
            ignore = False
            if self._sphinx_mode:
                for m in self.SPHINX_IGNORES_REGEX:
                    if m.match(error.message):
                        ignore = True
                        break
            if not ignore:
                yield (error.line, 'D000', error.message)


class CheckKnownDirectives(ContentCheck):
    REPORTS = frozenset(["D006"])

    def __init__(self, cfg):
        super(CheckKnownDirectives, self).__init__(cfg)
        self._sphinx_mode = cfg.get('sphinx')

    def report_iter(self, parsed_file):
        if parsed_file.extension.lower() == '.rst':
            lines = list(parsed_file.lines_iter())
            directives, directive_names = _extract_directives(lines)
            nodes_lines, first_line = _extract_node_lines(parsed_file.document)
            for node, (start, stop) in nodes_lines:
                for directive in six.iteritems(_RST_DIRECTIVES_MAPPING):
                    directive_name, directive_cls = directive
                    if isinstance(node, directive_cls):
                        directive_names.discard(directive_name)
                        break
            known_directives = set(six.iterkeys(_RST_DIRECTIVES_MAPPING))
            known_directives.update(_RST_DIRECTIVES_EXTRA)
            if self._sphinx_mode:
                known_directives.update(_SPHINX_RST_DIRECTIVES)
            for directive_name, start, end in directives:
                if not directive_name:
                    continue
                if directive_name not in known_directives:
                    yield (start + 1, 'D006',
                           "Unknown directive '%s'" % directive_name)


class CheckMaxLineLength(ContentCheck):
    REPORTS = frozenset(["D001"])

    def __init__(self, cfg):
        super(CheckMaxLineLength, self).__init__(cfg)
        self._max_line_length = self._cfg['max_line_length']
        self._allow_long_titles = self._cfg['allow_long_titles']

    def _txt_checker(self, parsed_file):
        for i, line in enumerate(parsed_file.lines_iter()):
            if len(line) > self._max_line_length:
                if not utils.contains_url(line):
                    yield (i + 1, 'D001', 'Line too long')

    def _rst_checker(self, parsed_file):
        lines = list(parsed_file.lines_iter())
        nodes_lines, first_line = _extract_node_lines(parsed_file.document)
        directives, _directive_names = _extract_directives(lines)

        def find_containing_nodes(line_num):
            if line_num < first_line and len(nodes_lines):
                return [nodes_lines[0][0]]
            contained_in = []
            for (n, (line_min, line_max)) in nodes_lines:
                if line_num >= line_min and line_num <= line_max:
                    contained_in.append((n, (line_min, line_max)))
            smallest_span = None
            best_nodes = []
            for (n, (line_min, line_max)) in contained_in:
                span = line_max - line_min
                if smallest_span is None:
                    smallest_span = span
                    best_nodes = [n]
                elif span < smallest_span:
                    smallest_span = span
                    best_nodes = [n]
                elif span == smallest_span:
                    best_nodes.append(n)
            return best_nodes

        def is_in_a_directive(index):
            for _directive_name, start, end in directives:
                if index >= start and index <= end:
                    return True
            return False

        def any_types(nodes, types):
            return any([isinstance(n, types) for n in nodes])

        skip_types = (
            docutils_nodes.target,
            docutils_nodes.literal_block,
        )
        title_types = (
            docutils_nodes.title,
            docutils_nodes.subtitle,
            docutils_nodes.section,
        )
        for i, line in enumerate(lines):
            if len(line) > self._max_line_length:
                if is_in_a_directive(i):
                    continue
                stripped = line.lstrip()
                if ' ' not in stripped:
                    # No room to split even if we could.
                    continue
                if utils.contains_url(stripped):
                    continue
                nodes = find_containing_nodes(i + 1)
                if any_types(nodes, skip_types):
                    continue
                if self._allow_long_titles and any_types(nodes, title_types):
                    continue
                yield (i + 1, 'D001', 'Line too long')

    def report_iter(self, parsed_file):
        if parsed_file.extension.lower() != '.rst':
            checker_func = self._txt_checker
        else:
            checker_func = self._rst_checker
        for issue in checker_func(parsed_file):
            yield issue
