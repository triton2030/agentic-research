#!/usr/bin/env python3
"""Print the plain-text content of the first h1 in an HTML file."""

from html.parser import HTMLParser
from pathlib import Path
import sys


class FirstH1Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._capturing = False
        self._found = False
        self._parts: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        del attrs
        if not self._found and tag.lower() == "h1":
            self._capturing = True

    def handle_endtag(self, tag: str) -> None:
        if self._capturing and tag.lower() == "h1":
            self._capturing = False
            self._found = True

    def handle_data(self, data: str) -> None:
        if self._capturing:
            self._parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self._parts).split())


def main() -> None:
    parser = FirstH1Parser()
    parser.feed(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(parser.title)


if __name__ == "__main__":
    main()
