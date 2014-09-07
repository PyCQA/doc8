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

import errno
import os

import chardet
from docutils import frontend
from docutils import parsers as docutils_parser
from docutils import utils
import restructuredtext_lint as rl
import six


class ParsedFile(object):
    FALLBACK_ENCODING = 'utf-8'

    def __init__(self, filename, encoding=None):
        self._filename = filename
        self._content = None
        self._raw_content = None
        self._encoding = encoding
        self._doc = None
        self._errors = None
        self._lines = None
        self._extension = os.path.splitext(filename)[1]

    @property
    def errors(self):
        if self._errors is not None:
            return self._errors
        self._errors = rl.lint(self.contents, filepath=self.filename)
        return self._errors

    @property
    def document(self):
        if self._doc is None:
            # Use the rst parsers document output to do as much of the
            # validation as we can without resorting to custom logic (this
            # parser is what sphinx and others use anyway so it's hopefully
            # mature).
            parser_cls = docutils_parser.get_parser_class("rst")
            parser = parser_cls()
            defaults = {
                'halt_level': 5,
                'report_level': 5,
                'quiet': True,
                'file_insertion_enabled': False,
                'traceback': True,
                # Development use only.
                'dump_settings': False,
                'dump_internals': False,
                'dump_transforms': False,
            }
            opt = frontend.OptionParser(components=[parser], defaults=defaults)
            doc = utils.new_document(source_path=self.filename,
                                     settings=opt.get_default_values())
            parser.parse(self.contents, doc)
            self._doc = doc
        return self._doc

    def lines_iter(self, remove_trailing_newline=True):
        if self._lines is None:
            with open(self.filename, 'rb') as fh:
                self._lines = list(fh)
        for line in self._lines:
            line = six.text_type(line, encoding=self.encoding)
            if remove_trailing_newline and line.endswith("\n"):
                line = line[0:-1]
            yield line

    @property
    def extension(self):
        return self._extension

    @property
    def filename(self):
        return self._filename

    @property
    def encoding(self):
        if not self._encoding:
            encoding = chardet.detect(self.raw_contents)['encoding']
            if not encoding:
                encoding = self.FALLBACK_ENCODING
            self._encoding = encoding
        return self._encoding

    @property
    def raw_contents(self):
        if self._raw_content is None:
            with open(self.filename, 'rb') as fh:
                self._raw_content = fh.read()
        return self._raw_content

    @property
    def contents(self):
        if self._content is None:
            self._content = six.text_type(self.raw_contents,
                                          encoding=self.encoding)
        return self._content

    def __str__(self):
        return "%s (%s, %s chars, %s lines)" % (
            self.filename, self.encoding, len(self.contents),
            len(list(self.lines_iter())))


def parse(filename, encoding=None):
    if not os.path.isfile(filename):
        raise IOError(errno.ENOENT, 'File not found', filename)
    return ParsedFile(filename, encoding=encoding)
