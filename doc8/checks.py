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

import abc
import re

import six


@six.add_metaclass(abc.ABCMeta)
class ContentCheck(object):
    @abc.abstractmethod
    def report_iter(self, parsed_file):
        pass


@six.add_metaclass(abc.ABCMeta)
class LineCheck(object):
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


