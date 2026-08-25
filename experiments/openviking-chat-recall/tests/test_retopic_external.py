"""Focused portability proofs for retopic and anchor repair."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[3]
SCRIPTS = ROOT / "experiments" / "openviking-chat-recall" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_retopic_tasks as BUILD
import fix_anchors_after_retopic as FIX
import reanchor as REANCHOR


class ExternalRetopicTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.foreign = self.root / "foreign-project"
        self.corpus = self.foreign / "_ops" / "chat-recall" / "raw"
        self.topics = self.foreign / "_ops" / "chat-recall" / "topics"
        self.tasks = self.foreign / "work" / "retopic" / "tasks"
        self.map_path = self.foreign / "work" / "retopic" / "anchor-map.json"
        self.catalog = self.foreign / "work" / "topic-catalog.json"
        self.corpus.mkdir(parents=True)
        self.topics.mkdir(parents=True)
        self.catalog.parent.mkdir(parents=True)

        self.topic_ids = [f"foreign-topic-{index:02d}" for index in range(20)]
        self.catalog.write_text(
            json.dumps(
                {
                    "topics": [
                        {"id": topic, "title": f"Foreign topic {index:02d}"}
                        for index, topic in enumerate(self.topic_ids)
                    ]
                }
            ),
            encoding="utf-8",
        )
        for topic in self.topic_ids:
            (self.topics / f"{topic}.md").write_text(
                f"# {topic}\n", encoding="utf-8"
            )

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def record(text: str, topic: str | None, kind: str = "решение") -> str:
        suffix = f" — type: {kind}"
        if topic is not None:
            suffix += f" | topic: {topic}"
        return f'* 2026-08-25T12:00:00+00:00 — "{text}"{suffix}'

    def write_holder(
        self,
        path: Path,
        records: list[str],
        *,
        extra_frontmatter: list[str] | None = None,
    ) -> None:
        frontmatter = ["---", "session: foreign-session"]
        if extra_frontmatter:
            frontmatter.extend(extra_frontmatter)
        frontmatter.extend(["---", ""])
        path.write_text("\n".join(frontmatter + records) + "\n", encoding="utf-8")

    def test_builder_covers_all_typed_records_and_all_20_catalog_topics(self) -> None:
        holder = self.corpus / "foreign-holder.md"
        self.write_holder(
            holder,
            [
                self.record("has old topic", self.topic_ids[0]),
                self.record("typed but missing topic", None),
                self.record("has another old topic", self.topic_ids[1]),
                "* this is not a typed record",
            ],
        )

        self.assertEqual(
            BUILD.main(str(self.tasks), str(self.corpus), str(self.catalog)), 0
        )
        task = (self.tasks / "foreign-holder.txt").read_text(encoding="utf-8")

        self.assertEqual(task.count("### L"), 3)
        self.assertIn("### L6", task)
        for topic in self.topic_ids:
            self.assertIn(f"`{topic}` —", task)

    def test_builder_does_not_fallback_to_local_catalog_for_foreign_corpus(self) -> None:
        holder = self.corpus / "foreign-holder.md"
        self.write_holder(holder, [self.record("typed", None)])

        with self.assertRaises(ValueError):
            BUILD.main(str(self.tasks), str(self.corpus))
        self.assertFalse(self.tasks.exists())

    def test_builder_rejects_missing_foreign_corpus(self) -> None:
        missing = self.foreign / "missing-raw"

        with self.assertRaises(FileNotFoundError):
            BUILD.main(str(self.tasks), str(missing), str(self.catalog))
        self.assertFalse(self.tasks.exists())

    def test_reanchor_uses_explicit_foreign_corpus_roots_and_map(self) -> None:
        holder = self.corpus / "foreign-holder.md"
        self.write_holder(holder, [self.record("anchor me", self.topic_ids[0])])
        topic = self.topics / f"{self.topic_ids[0]}.md"
        topic.write_text("# foreign\n- Claim [foreign-holder.md#L5]\n", encoding="utf-8")

        self.assertEqual(
            REANCHOR.build_map(str(self.corpus), [str(self.topics)], str(self.map_path)),
            0,
        )
        anchor_map = json.loads(self.map_path.read_text(encoding="utf-8"))
        self.assertIn("foreign-holder.md#L5", anchor_map)

        lines = holder.read_text(encoding="utf-8").splitlines()
        lines.insert(4, "types: [retopic]")
        holder.write_text("\n".join(lines) + "\n", encoding="utf-8")

        self.assertEqual(
            REANCHOR.fix(str(self.corpus), [str(self.topics)], str(self.map_path)),
            0,
        )
        self.assertIn("foreign-holder.md#L6", topic.read_text(encoding="utf-8"))

    def test_foreign_post_retopic_repair_remaps_directory_snapshot(self) -> None:
        before = self.foreign / "before-raw"
        before.mkdir()
        old_record = self.record("same record", "legacy-topic")
        new_record = self.record("same record", self.topic_ids[0])
        self.write_holder(before / "foreign-holder.md", [old_record])
        self.write_holder(
            self.corpus / "foreign-holder.md",
            [new_record],
            extra_frontmatter=["topics:", "  - foreign-topic-00"],
        )
        topic = self.topics / f"{self.topic_ids[0]}.md"
        topic.write_text("# foreign\n- Claim [foreign-holder.md#L5]\n", encoding="utf-8")

        self.assertEqual(
            FIX.main(
                str(before),
                True,
                str(self.corpus),
                [str(self.topics)],
            ),
            0,
        )
        self.assertIn("foreign-holder.md#L7", topic.read_text(encoding="utf-8"))

    def test_foreign_reanchor_requires_explicit_map_destination(self) -> None:
        holder = self.corpus / "foreign-holder.md"
        self.write_holder(holder, [self.record("typed", self.topic_ids[0])])

        with self.assertRaises(ValueError):
            REANCHOR.build_map(str(self.corpus), [str(self.topics)])


if __name__ == "__main__":
    unittest.main()
