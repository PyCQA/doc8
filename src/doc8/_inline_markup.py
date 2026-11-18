# MIT License
#
# Copyright (c) 2026 Adam Dangoor
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from re import Match

from docutils import nodes
from docutils.parsers.rst.states import Inliner
from docutils.utils import escape2null


class InlineMarkupInliner(Inliner):
    """Look for inline literals left as text by the emphasis handlers."""

    # Docutils interpolates these patterns from the concrete class namespace.
    simplename = Inliner.simplename
    emailc = Inliner.emailc
    non_whitespace_after = Inliner.non_whitespace_after
    non_whitespace_escape_before = Inliner.non_whitespace_escape_before
    uric = Inliner.uric
    uri_end = Inliner.uri_end
    non_unescaped_whitespace_escape_before = (
        Inliner.non_unescaped_whitespace_escape_before
    )

    def __init__(self) -> None:
        super().__init__()
        self.dispatch = {
            **self.dispatch,
            # Docutils dispatches to unbound methods with the inliner as
            # the first argument. types-docutils models these as bound.
            "*": InlineMarkupInliner._emphasis,  # type: ignore[dict-item]
            "**": InlineMarkupInliner._emphasis,  # type: ignore[dict-item]
        }
        self.lines: list[int] = []
        self._paragraph_lines = 0

    def parse(
        self,
        text: str,
        lineno: int,
        memo,
        parent: nodes.Element,
    ):
        self._paragraph_lines = text.count("\n")
        return super().parse(text, lineno, memo, parent)

    def _emphasis(self, match: Match[str], lineno: int):
        delimiter = match["start"]
        handler = Inliner.strong if delimiter == "**" else Inliner.emphasis
        before, inlines, remaining, messages = handler(self, match, lineno)
        if inlines and isinstance(inlines[0], (nodes.strong, nodes.emphasis)):
            raw = inlines[0].rawsource
            body = raw[len(delimiter) : -len(delimiter)]
            offset = self._literal_offset(text=body)
            if offset is not None:
                # Docutils passes the unconsumed suffix of the paragraph to
                # each inline handler and keeps its original line number.
                span_offset = self._paragraph_lines - match.string.count("\n")
                self.lines.append(lineno + span_offset + before.count("\n") + offset)
        return before, inlines, remaining, messages

    def _literal_offset(self, *, text: str) -> int | None:
        escaped = escape2null(text)
        for match in self.patterns.initial.finditer(escaped):
            if match["start"] != "``" or self.quoted_start(match):
                continue
            end = self.patterns.literal.search(escaped[match.end("start") :])
            if end and end.start(1):
                return escaped.count("\n", 0, match.start("start"))
        return None
