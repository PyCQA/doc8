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

import os


def find_files(paths, extensions, ignored_paths):
    extensions = set(extensions)

    def extension_matches(path):
        _base, ext = os.path.splitext(path)
        return ext in extensions

    def path_ignored(path):
        return os.path.normpath(path) in ignored_paths

    for path in paths:
        if path_ignored(path):
            continue
        if os.path.isfile(path):
            if extension_matches(path):
                yield path
        elif os.path.isdir(path):
            for root, dirnames, filenames in os.walk(path):
                if path_ignored(root):
                    continue
                for filename in filenames:
                    path = os.path.join(root, filename)
                    if extension_matches(path) and not path_ignored(path):
                        yield path
        else:
            raise IOError('Invalid path: %s' % path)


def filtered_traverse(document, filter_func):
    for n in document.traverse(include_self=True):
        if filter_func(n):
            yield n


def contains_url(line):
    if "http://" in line or "https://" in line:
        return True
    return False


def has_any_node_type(node, node_types):
    n = node
    while n is not None:
        if isinstance(n, node_types):
            return True
        n = n.parent
    return False
