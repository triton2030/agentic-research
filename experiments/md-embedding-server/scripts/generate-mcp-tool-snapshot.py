#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/tool-signatures-snapshot.json"
TARGET = ROOT / "tests/golden/mcp-tool-snapshot.json"


def main() -> int:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    tools = data.get("tools")
    if not isinstance(tools, list) or len(tools) != 32:
        raise SystemExit("source snapshot must contain 32 tools")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    tmp = TARGET.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.move(str(tmp), TARGET)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
