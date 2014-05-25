# -*- coding: utf-8 -*-

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

import six

from docutils import core
from docutils import frontend
from docutils import nodes as docutils_nodes
from docutils import parsers as docutils_parser
from docutils import utils


class ParsedFile(object):
    def __init__(self, filename, encoding='utf8'):
        self._filename = filename
        self._content = None
        self._raw_content = None
        self._encoding = encoding
        self._doc = None
        self._errors = None
        self._defaults = {
            'input_encoding': self._encoding,
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

    @property
    def errors(self):
        if self._errors is not None:
            return self._errors
        # Borrowed from pypi package restructuredtext-lint but modified to work
        # better when there exists fatal/critical errors.
        pub = core.Publisher(None, None, None, settings=None)
        pub.set_components('standalone', 'restructuredtext', 'pseudoxml')
        defaults = dict(self._defaults)
        settings = pub.get_settings(**defaults)
        pub.set_io()
        reader = pub.reader
        document = utils.new_document(self.filename, settings)
        document.reporter.stream = None
        # Collect errors via an observer
        errors = []
        def error_collector(data):
            # Mutate the data since it was just generated
            data.line = data['line']
            data.source = data['source']
            data.level = data['level']
            data.type = data['type']
            data.message = docutils_nodes.Element.astext(data.children[0])
            data.full_message = docutils_nodes.Element.astext(data)
            # Save the error
            errors.append(data)
        document.reporter.attach_observer(error_collector)
        reader.parser.parse(self.contents, document)
        document.transformer.populate_from_components(
            (pub.source, pub.reader, pub.reader.parser, pub.writer,
             pub.destination))
        transformer = document.transformer
        while transformer.transforms:
            if not transformer.sorted:
                # Unsorted initially, and whenever a transform is added.
                transformer.transforms.sort()
                transformer.transforms.reverse()
                transformer.sorted = True
            transform = transformer.transforms.pop()
            priority, transform_class, pending, kwargs = transform
            transform = transform_class(transformer.document,
                                        startnode=pending)
            transform.apply(**kwargs)
            transformer.applied.append((priority, transform_class,
                                        pending, kwargs))
        self._errors = errors
        return errors

    @property
    def document(self):
        if self._doc is None:
            # Use the rst parsers document output to do as much of the
            # validation as we can without resorting to custom logic (this
            # parser is what sphinx and others use anyway so it's hopefully
            # mature).
            parser_cls = docutils_parser.get_parser_class("rst")
            parser = parser_cls()
            defaults = dict(self._defaults)
            opt = frontend.OptionParser(components=[parser], defaults=defaults)
            doc = utils.new_document(source_path=self.filename,
                                     settings=opt.get_default_values())
            parser.parse(self.contents, doc)
            self._doc = doc
        return self._doc

    def lines_iter(self, remove_trailing_newline=True):
        with open(self.filename, 'rb') as fh:
            for line in fh:
                line = six.text_type(line, encoding=self.encoding)
                if remove_trailing_newline and line.endswith("\n"):
                    line = line[0:-1]
                yield line

    @property
    def filename(self):
        return self._filename

    @property
    def encoding(self):
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


def parse(filename, encoding="utf8"):
    if not os.path.isfile(filename):
        raise IOError(errno.ENOENT, 'File not found', filename)
    return ParsedFile(filename, encoding=encoding)
