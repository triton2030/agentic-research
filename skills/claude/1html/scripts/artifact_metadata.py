#!/usr/bin/env python3
"""Print gallery metadata and the first h1 fallback from an HTML artifact."""

from html.parser import HTMLParser
from pathlib import Path
import re
import sys


class ArtifactMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._capturing_h1 = False
        self._found_h1 = False
        self._h1_parts: list[str] = []
        self._title_override = ""
        self._icon = ""

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        normalized_tag = tag.lower()
        attributes = {name.lower(): value or "" for name, value in attrs}

        if normalized_tag == "meta":
            name = attributes.get("name", "").lower()
            content = " ".join(attributes.get("content", "").split())
            if name == "artifact-title" and not self._title_override:
                self._title_override = content
            elif name == "artifact-icon" and not self._icon:
                self._icon = content
        elif not self._found_h1 and normalized_tag == "h1":
            self._capturing_h1 = True

    def handle_endtag(self, tag: str) -> None:
        if self._capturing_h1 and tag.lower() == "h1":
            self._capturing_h1 = False
            self._found_h1 = True

    def handle_data(self, data: str) -> None:
        if self._capturing_h1:
            self._h1_parts.append(data)

    @property
    def title(self) -> str:
        if self._title_override:
            return self._title_override
        return " ".join("".join(self._h1_parts).split())

    @property
    def icon(self) -> str:
        if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", self._icon):
            return self._icon
        return ""


def main() -> None:
    parser = ArtifactMetadataParser()
    parser.feed(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(f"{parser.title}\t{parser.icon}")


if __name__ == "__main__":
    main()
