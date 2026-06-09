from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import navigator


ROOT = Path(__file__).resolve().parents[1]


def _write_coherence_corpus(tmp_path: Path) -> tuple[Path, Path]:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    source = corpus / "source.md"
    source.write_text(
        "\n".join(
            [
                "---",
                "description: ignored by coherence audit",
                "depends-on:",
                "  - [[target#Alpha]]",
                "---",
                "# Source",
                "",
                "First claim [[target#Alpha]] keeps moving.",
                "",
                "Middle claim [[target#Gamma]]. Bare [[target]].",
                "",
                "Last claim [[other#Beta]].",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (corpus / "target.md").write_text(
        "\n".join(
            [
                "# Target",
                "",
                "## Alpha",
                "",
                "Alpha explains the first claim with [[other#Beta]].",
                "",
                "## Gamma",
                "",
                "Gamma explains the middle claim.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (corpus / "other.md").write_text(
        "\n".join(
            [
                "# Other",
                "",
                "## Beta",
                "",
                "Beta supports the final claim.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return corpus, source


def test_coherence_audit_inserts_blocks_immediately_after_each_anchored_wikilink(
    tmp_path: Path,
) -> None:
    corpus, source = _write_coherence_corpus(tmp_path)

    payload = navigator.coherence_audit(str(source), scan=str(corpus), depth=2)

    assert payload["command"] == "coherence-audit"
    assert payload["stats"]["blocks_expanded"] == 4
    assert payload["stats"]["skipped_bare_wikilinks"] == 1
    assert payload["issues"] == []
    assert "description: ignored" not in payload["text"]
    first_link = payload["text"].index("[[target#Alpha]]")
    first_marker = payload["text"].index("md-coherence-audit link=0")
    middle_link = payload["text"].index("[[target#Gamma]]")
    middle_marker = payload["text"].index("md-coherence-audit link=2")
    final_link = payload["text"].rindex("[[other#Beta]]")
    final_marker = payload["text"].rindex("md-coherence-audit link=3")
    assert first_link < first_marker < middle_link < middle_marker < final_link < final_marker
    assert "[[target#Gamma]].\n\n<!-- md-coherence-audit link=2" in payload["text"]
    assert "Alpha explains the first claim" in payload["text"]
    assert "Gamma explains the middle claim" in payload["text"]
    assert "Beta supports the final claim" in payload["text"]


def test_coherence_audit_cli_emits_json_envelope(tmp_path: Path) -> None:
    corpus, source = _write_coherence_corpus(tmp_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "md_cli",
            "coherence-audit",
            str(source),
            "--scan",
            str(corpus),
            "--json",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["_envelope"]["tool"] == "md_coherence_audit"
    assert payload["command"] == "coherence-audit"
