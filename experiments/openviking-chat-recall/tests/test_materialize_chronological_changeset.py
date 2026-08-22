from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = EXPERIMENT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import materialize_chronological_changeset as materializer  # noqa: E402


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


class MaterializeChronologicalChangesetTests(unittest.TestCase):
    def _fixture(self, root: Path) -> dict[str, Path | dict]:
        repo = root / "repo"
        wiki = repo / "artifacts/chronological-pilot/current/wiki"
        batch = repo / "artifacts/chronological-pilot/batch-003"
        evidence_path = repo / "artifacts/full-build/evidence/records.jsonl"
        manifest_path = repo / "artifacts/chronological-pilot/batch-003-input.json"
        receipt_path = batch / "receipt.json"
        changeset_path = batch / "changeset.json"

        old_page = (
            "---\n"
            "type: method\n"
            "title: Как сохранять owner quotes?\n"
            "description: Source-bound capture.\n"
            "---\n\n"
            "# Как сохранять owner quotes?\n\n"
            "Сохраняй слова владельца отдельно.\n"
        ).encode("utf-8")
        index = (
            "---\n"
            "type: index\n"
            "title: Test Wiki\n"
            "description: Routes.\n"
            "---\n\n"
            "# Test Wiki\n\n"
            "- [Как сохранять owner quotes?](method/owner-quotes.md)\n"
        ).encode("utf-8")
        (wiki / "method").mkdir(parents=True)
        (wiki / "method/owner-quotes.md").write_bytes(old_page)
        (wiki / "index.md").write_bytes(index)

        evidence = [
            {
                "record_id": "cr-0000000000000001",
                "source_address": "_ops/chat-recall/a.md:15",
                "source_path": "_ops/chat-recall/a.md",
                "source_line": 15,
                "quote": "Сохраняй слова владельца с точным адресом источника; не заменяй его пересказом агента.",
            },
            {
                "record_id": "cr-0000000000000002",
                "source_address": "_ops/chat-recall/b.md:16",
                "source_path": "_ops/chat-recall/b.md",
                "source_line": 16,
                "quote": "Глобальная инструкция должна описывать желаемый результат.",
            },
        ]
        evidence_path.parent.mkdir(parents=True)
        evidence_raw = b"".join(
            json.dumps(item, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n"
            for item in evidence
        )
        evidence_path.write_bytes(evidence_raw)

        manifest = {
            "schema": "openviking-chat-recall/chronological-batch-input.v3",
            "batch_id": "batch-003",
            "previous_batch_id": "batch-002",
            "corpus_commit": "1" * 40,
            "evidence_commit": "2" * 40,
            "evidence_records_sha256": _sha(evidence_raw),
            "time_boundary_utc": "2026-08-01T00:00:00+00:00",
            "holders": [
                {
                    "source_path": "_ops/chat-recall/a.md",
                    "record_ids": ["cr-0000000000000001"],
                },
                {
                    "source_path": "_ops/chat-recall/b.md",
                    "record_ids": ["cr-0000000000000002"],
                },
            ],
            "counts": {
                "holder_count": 2,
                "record_count": 2,
                "diagnostic_record_count": 0,
                "source_quote_chars": sum(len(item["quote"]) for item in evidence),
                "source_quote_utf8_bytes": sum(
                    len(item["quote"].encode("utf-8")) for item in evidence
                ),
            },
        }
        manifest_raw = _json_bytes(manifest)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(manifest_raw)

        updated_page = (
            "---\n"
            "type: method\n"
            "title: Как сохранять owner quotes?\n"
            "description: Source-bound capture.\n"
            "---\n\n"
            "# Как сохранять owner quotes?\n\n"
            "Сохраняй слова владельца с точным адресом источника.\n\n"
            "## Sources\n\n"
            "- [source](../../../../../_ops/chat-recall/a.md#L15)\n"
        )
        instruction_page = (
            "---\n"
            "type: method\n"
            "title: Как писать глобальную инструкцию?\n"
            "description: Owner-specific outcome.\n"
            "---\n\n"
            "# Как писать глобальную инструкцию?\n\n"
            "Глобальная инструкция описывает желаемый результат.\n\n"
            "## Sources\n\n"
            "- [source](../../../../../_ops/chat-recall/b.md#L16)\n"
        )
        updated_index = (
            "---\n"
            "type: index\n"
            "title: Test Wiki\n"
            "description: Routes.\n"
            "---\n\n"
            "# Test Wiki\n\n"
            "- [Как сохранять owner quotes?](method/owner-quotes.md)\n"
            "- [Как писать глобальную инструкцию?](method/global-instruction.md)\n"
        )

        def claim(
            claim_id: str,
            statement: str,
            record_id: str,
            question: str,
        ) -> dict:
            return {
                "claim_id": claim_id,
                "statement": statement,
                "epistemic_kind": "source-backed",
                "supporting_record_ids": [record_id],
                "page_fit": {
                    "page_question": question,
                    "answering_record_ids": [record_id],
                    "reason": "The source directly answers this page question.",
                },
            }

        changeset = {
            "schema": "openviking-chat-recall/chronological-wiki-changeset.v3",
            "phase": "semantic-draft",
            "status": "accepted",
            "batch_id": "batch-003",
            "previous_batch_id": "batch-002",
            "model": "gpt-5.6-luna",
            "thinking": "max",
            "input": {
                "manifest_path": manifest_path.relative_to(repo).as_posix(),
                "manifest_sha256": _sha(manifest_raw),
                "evidence_records_path": evidence_path.relative_to(repo).as_posix(),
                "evidence_records_sha256": _sha(evidence_raw),
                "corpus_commit": manifest["corpus_commit"],
                "evidence_commit": manifest["evidence_commit"],
                "time_boundary_utc": manifest["time_boundary_utc"],
            },
            "prior_checkpoint": {
                "wiki_root": wiki.relative_to(repo).as_posix(),
                "wiki_tree_sha256_target": materializer.tree_digest(wiki)[0],
            },
            "allowed_operations": [
                "create",
                "update",
                "supersede",
                "no-change",
                "reject",
            ],
            "frozen_record_ids_in_manifest_order": [
                "cr-0000000000000001",
                "cr-0000000000000002",
            ],
            "operations": [
                {
                    "operation": "update",
                    "page_path": "current/wiki/method/owner-quotes.md",
                    "page_type": "method",
                    "prior_sha256": _sha(old_page),
                    "proposed_content": updated_page,
                    "proposed_sha256": _sha(updated_page.encode("utf-8")),
                    "record_ids": ["cr-0000000000000001"],
                    "material_claims": [
                        claim(
                            "owner-source-address",
                            "Owner quotes retain an exact source address.",
                            "cr-0000000000000001",
                            "Как сохранять owner quotes?",
                        )
                    ],
                },
                {
                    "operation": "create",
                    "page_path": "current/wiki/method/global-instruction.md",
                    "page_type": "method",
                    "prior_sha256": None,
                    "proposed_content": instruction_page,
                    "proposed_sha256": _sha(instruction_page.encode("utf-8")),
                    "record_ids": ["cr-0000000000000002"],
                    "material_claims": [
                        claim(
                            "instruction-outcome",
                            "A global instruction states the desired outcome.",
                            "cr-0000000000000002",
                            "Как писать глобальную инструкцию?",
                        )
                    ],
                },
                {
                    "operation": "update",
                    "page_path": "current/wiki/index.md",
                    "page_type": "index",
                    "prior_sha256": _sha(index),
                    "proposed_content": updated_index,
                    "proposed_sha256": _sha(updated_index.encode("utf-8")),
                    "record_ids": [],
                    "material_claims": [],
                },
            ],
            "coverage": [
                {
                    "record_id": "cr-0000000000000001",
                    "disposition": "used",
                    "page_path": "current/wiki/method/owner-quotes.md",
                    "reason": "Updates the existing capture question.",
                },
                {
                    "record_id": "cr-0000000000000002",
                    "disposition": "used",
                    "page_path": "current/wiki/method/global-instruction.md",
                    "reason": "Creates the distinct instruction question.",
                },
            ],
            "gaps": [],
        }
        batch.mkdir(parents=True)
        changeset_raw = _json_bytes(changeset)
        changeset_path.write_bytes(changeset_raw)
        return {
            "repo": repo,
            "wiki": wiki,
            "manifest": manifest_path,
            "evidence": evidence_path,
            "receipt": receipt_path,
            "changeset": changeset_path,
            "changeset_value": changeset,
            "accepted_sha": _sha(changeset_raw),
        }

    def _upgrade_to_v4(self, fixture: dict) -> None:
        repo = fixture["repo"]
        manifest_value = json.loads(fixture["manifest"].read_text(encoding="utf-8"))
        manifest_value["batch_id"] = "batch-004"
        manifest_value["previous_batch_id"] = "batch-003"
        manifest_path = repo / "artifacts/chronological-pilot/batch-004-input.json"
        manifest_raw = _json_bytes(manifest_value)
        manifest_path.write_bytes(manifest_raw)

        changeset = copy.deepcopy(fixture["changeset_value"])
        changeset["schema"] = "openviking-chat-recall/chronological-wiki-changeset.v4"
        changeset["batch_id"] = "batch-004"
        changeset["previous_batch_id"] = "batch-003"
        changeset["input"]["manifest_path"] = manifest_path.relative_to(repo).as_posix()
        changeset["input"]["manifest_sha256"] = _sha(manifest_raw)

        allocation = {
            "schema": "openviking-chat-recall/chronological-wiki-allocation.v1",
            "status": "accepted",
            "batch_id": "batch-004",
            "manifest_path": manifest_path.relative_to(repo).as_posix(),
            "manifest_sha256": _sha(manifest_raw),
            "evidence_records_sha256": changeset["input"][
                "evidence_records_sha256"
            ],
            "prior_wiki_tree_sha256": changeset["prior_checkpoint"][
                "wiki_tree_sha256_target"
            ],
            "pages": [
                {
                    "operation": "update",
                    "page_path": "current/wiki/method/owner-quotes.md",
                    "page_type": "method",
                    "h1": "Как сохранять owner quotes?",
                },
                {
                    "operation": "create",
                    "page_path": "current/wiki/method/global-instruction.md",
                    "page_type": "method",
                    "h1": "Как писать глобальную инструкцию?",
                },
            ],
            "records": [
                {
                    "record_id": "cr-0000000000000001",
                    "source_address": "_ops/chat-recall/a.md:15",
                    "source_owner": "owner",
                    "source_scope": "agentic-research",
                    "disposition": "used",
                    "target_page_path": "current/wiki/method/owner-quotes.md",
                    "reason": "Updates the owner-quote page.",
                },
                {
                    "record_id": "cr-0000000000000002",
                    "source_address": "_ops/chat-recall/b.md:16",
                    "source_owner": "owner",
                    "source_scope": "agentic-research",
                    "disposition": "used",
                    "target_page_path": "current/wiki/method/global-instruction.md",
                    "reason": "Creates the global-instruction page.",
                },
            ],
        }
        allocation_path = fixture["changeset"].parent / "allocation.json"
        allocation_raw = _json_bytes(allocation)
        allocation_path.write_bytes(allocation_raw)
        allocation_sha = _sha(allocation_raw)
        changeset["input"]["allocation_path"] = allocation_path.relative_to(repo).as_posix()
        changeset["input"]["allocation_sha256"] = allocation_sha

        changeset_raw = _json_bytes(changeset)
        fixture.update(
            {
                "manifest": manifest_path,
                "changeset_value": changeset,
                "accepted_sha": _sha(changeset_raw),
                "allocation": allocation_path,
                "allocation_value": allocation,
                "accepted_allocation_sha": allocation_sha,
            }
        )
        fixture["changeset"].write_bytes(changeset_raw)

    def _write_changeset(self, fixture: dict, changeset: dict) -> None:
        raw = _json_bytes(changeset)
        fixture["changeset"].write_bytes(raw)
        fixture["changeset_value"] = changeset
        fixture["accepted_sha"] = _sha(raw)

    def _write_allocation(self, fixture: dict, allocation: dict) -> None:
        raw = _json_bytes(allocation)
        fixture["allocation"].write_bytes(raw)
        fixture["allocation_value"] = allocation
        fixture["accepted_allocation_sha"] = _sha(raw)
        changeset = copy.deepcopy(fixture["changeset_value"])
        changeset["input"]["allocation_sha256"] = _sha(raw)
        self._write_changeset(fixture, changeset)

    @staticmethod
    def _snapshot(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    def _materialize(self, fixture: dict, *, dry_run: bool = False) -> dict:
        return materializer.materialize(
            repo_root=fixture["repo"],
            changeset_path=fixture["changeset"],
            manifest_path=fixture["manifest"],
            evidence_records_path=fixture["evidence"],
            wiki_root=fixture["wiki"],
            receipt_path=fixture["receipt"],
            accepted_changeset_sha256=fixture["accepted_sha"],
            allocation_path=fixture.get("allocation"),
            accepted_allocation_sha256=fixture.get("accepted_allocation_sha"),
            dry_run=dry_run,
        )

    def test_materializes_exact_bytes_and_machine_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = self._fixture(Path(temp_dir))
            dry_first = self._materialize(fixture, dry_run=True)
            dry_second = self._materialize(fixture, dry_run=True)
            self.assertEqual(dry_first, dry_second)
            self.assertFalse(fixture["receipt"].exists())

            receipt = self._materialize(fixture)
            stored = json.loads(fixture["receipt"].read_text(encoding="utf-8"))

            self.assertEqual(receipt, stored)
            self.assertEqual(receipt["status"], "materialized-candidate")
            self.assertEqual(
                receipt["coverage"],
                {
                    "total": 2,
                    "used": 2,
                    "reject": 0,
                    "skipped": 0,
                    "record_ids_in_manifest_order": [
                        "cr-0000000000000001",
                        "cr-0000000000000002",
                    ],
                },
            )
            self.assertEqual(receipt["operations"]["create"], 1)
            self.assertEqual(receipt["operations"]["update"], 2)
            self.assertEqual(receipt["tree_digest"]["after"]["sha256"], materializer.tree_digest(fixture["wiki"])[0])
            changeset = fixture["changeset_value"]
            for operation in changeset["operations"]:
                target = fixture["wiki"] / Path(operation["page_path"]).relative_to("current/wiki")
                self.assertEqual(target.read_text(encoding="utf-8"), operation["proposed_content"])

    def test_v3_batch_004_is_rejected_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = self._fixture(Path(temp_dir))
            before = self._snapshot(fixture["wiki"])
            changeset = copy.deepcopy(fixture["changeset_value"])
            changeset["batch_id"] = "batch-004"
            self._write_changeset(fixture, changeset)

            with self.assertRaisesRegex(
                materializer.MaterializationError,
                "v3 changeset is supported only for batch-003",
            ):
                self._materialize(fixture)
            self.assertEqual(before, self._snapshot(fixture["wiki"]))
            self.assertFalse(fixture["receipt"].exists())

    def test_v4_allocation_dry_run_and_materialization_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = self._fixture(Path(temp_dir))
            self._upgrade_to_v4(fixture)

            dry_receipt = self._materialize(fixture, dry_run=True)
            self.assertEqual(
                dry_receipt["schema"],
                "openviking-chat-recall/chronological-wiki-receipt.v4",
            )
            self.assertEqual(
                dry_receipt["source_snapshot"]["allocation_path"],
                fixture["allocation"].relative_to(fixture["repo"]).as_posix(),
            )
            self.assertEqual(
                dry_receipt["source_snapshot"]["allocation_sha256"],
                fixture["accepted_allocation_sha"],
            )
            self.assertFalse(fixture["receipt"].exists())

            receipt = self._materialize(fixture)
            self.assertEqual(receipt, json.loads(fixture["receipt"].read_text()))
            self.assertEqual(
                receipt["tree_digest"]["after"]["sha256"],
                materializer.tree_digest(fixture["wiki"])[0],
            )

    def test_v4_requires_allocation_arguments_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = self._fixture(Path(temp_dir))
            self._upgrade_to_v4(fixture)
            before = self._snapshot(fixture["wiki"])
            fixture.pop("allocation")
            fixture.pop("accepted_allocation_sha")

            with self.assertRaisesRegex(
                materializer.MaterializationError,
                "v4 changeset requires allocation_path",
            ):
                self._materialize(fixture)
            self.assertEqual(before, self._snapshot(fixture["wiki"]))
            self.assertFalse(fixture["receipt"].exists())

    def test_v4_rejects_semantic_record_moved_off_allocated_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = self._fixture(Path(temp_dir))
            self._upgrade_to_v4(fixture)
            before = self._snapshot(fixture["wiki"])
            changeset = copy.deepcopy(fixture["changeset_value"])
            owner_operation = changeset["operations"][0]
            instruction_operation = changeset["operations"][1]
            moved_record_id = "cr-0000000000000002"

            owner_operation["record_ids"].append(moved_record_id)
            moved_claim = copy.deepcopy(instruction_operation["material_claims"][0])
            moved_claim["page_fit"]["page_question"] = "Как сохранять owner quotes?"
            owner_operation["material_claims"].append(moved_claim)
            owner_content = owner_operation["proposed_content"] + (
                "- [instruction source](../../../../../_ops/chat-recall/b.md#L16)\n"
            )
            owner_operation["proposed_content"] = owner_content
            owner_operation["proposed_sha256"] = _sha(owner_content.encode("utf-8"))

            instruction_content = instruction_operation["proposed_content"].replace(
                "- [source](../../../../../_ops/chat-recall/b.md#L16)\n", ""
            )
            instruction_operation["proposed_content"] = instruction_content
            instruction_operation["proposed_sha256"] = _sha(
                instruction_content.encode("utf-8")
            )
            instruction_operation["record_ids"] = []
            instruction_operation["material_claims"] = []
            changeset["coverage"][1]["page_path"] = (
                "current/wiki/method/owner-quotes.md"
            )
            self._write_changeset(fixture, changeset)

            with self.assertRaisesRegex(
                materializer.MaterializationError,
                "allocation target mismatch",
            ):
                self._materialize(fixture)
            self.assertEqual(before, self._snapshot(fixture["wiki"]))
            self.assertFalse(fixture["receipt"].exists())

    def test_v4_allocation_hash_path_h1_and_disposition_drift_fail_before_write(self) -> None:
        for mode, message in (
            ("hash", "accepted allocation SHA mismatch"),
            ("path", "allocation path does not match changeset input"),
            ("h1", "allocation page map does not match"),
            ("disposition", "allocation disposition does not match coverage"),
        ):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temp_dir:
                fixture = self._fixture(Path(temp_dir))
                self._upgrade_to_v4(fixture)
                before = self._snapshot(fixture["wiki"])
                if mode == "hash":
                    fixture["accepted_allocation_sha"] = "0" * 64
                elif mode == "path":
                    changeset = copy.deepcopy(fixture["changeset_value"])
                    changeset["input"]["allocation_path"] = (
                        "artifacts/chronological-pilot/batch-004/wrong.json"
                    )
                    self._write_changeset(fixture, changeset)
                else:
                    allocation = copy.deepcopy(fixture["allocation_value"])
                    if mode == "h1":
                        allocation["pages"][1]["h1"] = "Другая страница?"
                    else:
                        allocation["records"][1]["disposition"] = "skipped"
                        allocation["records"][1]["target_page_path"] = None
                    self._write_allocation(fixture, allocation)

                with self.assertRaisesRegex(materializer.MaterializationError, message):
                    self._materialize(fixture)
                self.assertEqual(before, self._snapshot(fixture["wiki"]))
                self.assertFalse(fixture["receipt"].exists())

    def test_v2_or_missing_page_fit_fails_before_write(self) -> None:
        for mutation, message in (
            (lambda value: value.__setitem__("schema", "openviking-chat-recall/chronological-wiki-changeset.v2"), "schema"),
            (lambda value: value["operations"][0]["material_claims"][0].pop("page_fit"), "page_fit"),
        ):
            with self.subTest(message=message), tempfile.TemporaryDirectory() as temp_dir:
                fixture = self._fixture(Path(temp_dir))
                before = self._snapshot(fixture["wiki"])
                value = copy.deepcopy(fixture["changeset_value"])
                mutation(value)
                raw = _json_bytes(value)
                fixture["changeset"].write_bytes(raw)
                fixture["accepted_sha"] = _sha(raw)
                with self.assertRaisesRegex(materializer.MaterializationError, message):
                    self._materialize(fixture)
                self.assertEqual(before, self._snapshot(fixture["wiki"]))
                self.assertFalse(fixture["receipt"].exists())

    def test_candidate_can_be_preflighted_but_not_materialized(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = self._fixture(Path(temp_dir))
            before = self._snapshot(fixture["wiki"])
            value = copy.deepcopy(fixture["changeset_value"])
            value["status"] = "candidate"
            raw = _json_bytes(value)
            fixture["changeset"].write_bytes(raw)
            fixture["accepted_sha"] = _sha(raw)

            receipt = self._materialize(fixture, dry_run=True)
            self.assertEqual(receipt["status"], "materialized-candidate")
            with self.assertRaisesRegex(
                materializer.MaterializationError,
                "cannot be materialized before acceptance",
            ):
                self._materialize(fixture)
            self.assertEqual(before, self._snapshot(fixture["wiki"]))
            self.assertFalse(fixture["receipt"].exists())

    def test_path_prior_and_content_sha_fail_before_write(self) -> None:
        cases = (
            (lambda value: value["operations"][1].__setitem__("page_path", "current/wiki/../escape.md"), "path"),
            (lambda value: value["operations"][0].__setitem__("prior_sha256", "0" * 64), "prior SHA"),
            (lambda value: value["operations"][0].__setitem__("proposed_sha256", "0" * 64), "proposed SHA"),
            (
                lambda value: value["operations"][0]["record_ids"].append(
                    "cr-ffffffffffffffff"
                ),
                "invalid record_ids",
            ),
            (
                lambda value: value["operations"][2]["record_ids"].append(
                    "cr-0000000000000001"
                ),
                "index operation",
            ),
        )
        for mutation, message in cases:
            with self.subTest(message=message), tempfile.TemporaryDirectory() as temp_dir:
                fixture = self._fixture(Path(temp_dir))
                before = self._snapshot(fixture["wiki"])
                value = copy.deepcopy(fixture["changeset_value"])
                mutation(value)
                raw = _json_bytes(value)
                fixture["changeset"].write_bytes(raw)
                fixture["accepted_sha"] = _sha(raw)
                with self.assertRaisesRegex(materializer.MaterializationError, message):
                    self._materialize(fixture)
                self.assertEqual(before, self._snapshot(fixture["wiki"]))
                self.assertFalse(fixture["receipt"].exists())

    def test_named_split_requires_one_source_operation_and_one_create(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = self._fixture(Path(temp_dir))
            value = copy.deepcopy(fixture["changeset_value"])
            value["operations"][0]["split_group_id"] = "split-owner-instruction"
            value["operations"][1]["split_group_id"] = "split-owner-instruction"
            raw = _json_bytes(value)
            fixture["changeset"].write_bytes(raw)
            fixture["accepted_sha"] = _sha(raw)
            receipt = self._materialize(fixture, dry_run=True)
            self.assertEqual(receipt["split_groups"], ["split-owner-instruction"])

        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = self._fixture(Path(temp_dir))
            before = self._snapshot(fixture["wiki"])
            value = copy.deepcopy(fixture["changeset_value"])
            value["operations"][1]["split_group_id"] = "split-owner-instruction"
            raw = _json_bytes(value)
            fixture["changeset"].write_bytes(raw)
            fixture["accepted_sha"] = _sha(raw)
            with self.assertRaisesRegex(materializer.MaterializationError, "split_group_id"):
                self._materialize(fixture)
            self.assertEqual(before, self._snapshot(fixture["wiki"]))

    def test_reject_disposition_cannot_be_materialized(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = self._fixture(Path(temp_dir))
            before = self._snapshot(fixture["wiki"])
            value = copy.deepcopy(fixture["changeset_value"])
            value["coverage"][1]["disposition"] = "reject"
            raw = _json_bytes(value)
            fixture["changeset"].write_bytes(raw)
            fixture["accepted_sha"] = _sha(raw)
            with self.assertRaisesRegex(
                materializer.MaterializationError,
                "used coverage does not exactly match",
            ):
                self._materialize(fixture)
            self.assertEqual(before, self._snapshot(fixture["wiki"]))
            self.assertFalse(fixture["receipt"].exists())

    def test_used_record_requires_material_claim_responsibility(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = self._fixture(Path(temp_dir))
            before = self._snapshot(fixture["wiki"])
            value = copy.deepcopy(fixture["changeset_value"])
            value["operations"][0]["material_claims"] = []
            raw = _json_bytes(value)
            fixture["changeset"].write_bytes(raw)
            fixture["accepted_sha"] = _sha(raw)

            with self.assertRaisesRegex(
                materializer.MaterializationError,
                "record_ids do not exactly match material claim support",
            ):
                self._materialize(fixture)
            self.assertEqual(before, self._snapshot(fixture["wiki"]))
            self.assertFalse(fixture["receipt"].exists())

    def test_only_exactly_cited_prior_evidence_can_move_during_update(self) -> None:
        for prior_linked, expected in ((True, None), (False, "outside the batch")):
            with self.subTest(prior_linked=prior_linked), tempfile.TemporaryDirectory() as temp_dir:
                fixture = self._fixture(Path(temp_dir))
                prior_record = {
                    "record_id": "cr-0000000000000003",
                    "source_address": "_ops/chat-recall/c.md:17",
                    "source_path": "_ops/chat-recall/c.md",
                    "source_line": 17,
                    "quote": "Ранее принятое знание можно перенести в отдельную страницу при явном split.",
                }
                evidence_raw = fixture["evidence"].read_bytes() + (
                    json.dumps(prior_record, ensure_ascii=False, sort_keys=True).encode(
                        "utf-8"
                    )
                    + b"\n"
                )
                fixture["evidence"].write_bytes(evidence_raw)

                old_path = fixture["wiki"] / "method/owner-quotes.md"
                if prior_linked:
                    old_path.write_text(
                        old_path.read_text(encoding="utf-8")
                        + "\n## Sources\n\n"
                        + "- [prior](../../../../../_ops/chat-recall/c.md#L17)\n",
                        encoding="utf-8",
                    )

                manifest_value = json.loads(
                    fixture["manifest"].read_text(encoding="utf-8")
                )
                manifest_value["evidence_records_sha256"] = _sha(evidence_raw)
                manifest_raw = _json_bytes(manifest_value)
                fixture["manifest"].write_bytes(manifest_raw)

                value = copy.deepcopy(fixture["changeset_value"])
                value["input"]["evidence_records_sha256"] = _sha(evidence_raw)
                value["input"]["manifest_sha256"] = _sha(manifest_raw)
                value["prior_checkpoint"]["wiki_tree_sha256_target"] = (
                    materializer.tree_digest(fixture["wiki"])[0]
                )
                operation = value["operations"][0]
                operation["prior_sha256"] = _sha(old_path.read_bytes())
                operation["record_ids"].append(prior_record["record_id"])
                operation["material_claims"].append(
                    {
                        "claim_id": "prior-split-source",
                        "statement": "Accepted prior evidence remains addressable during a split.",
                        "epistemic_kind": "source-backed",
                        "supporting_record_ids": [prior_record["record_id"]],
                        "page_fit": {
                            "page_question": "Как сохранять owner quotes?",
                            "answering_record_ids": [prior_record["record_id"]],
                            "reason": "The accepted source remains part of this page rewrite.",
                        },
                    }
                )
                content = operation["proposed_content"] + (
                    "- [prior](../../../../../_ops/chat-recall/c.md#L17)\n"
                )
                operation["proposed_content"] = content
                operation["proposed_sha256"] = _sha(content.encode("utf-8"))
                raw = _json_bytes(value)
                fixture["changeset"].write_bytes(raw)
                fixture["accepted_sha"] = _sha(raw)

                if expected is None:
                    receipt = self._materialize(fixture, dry_run=True)
                    self.assertEqual(receipt["coverage"]["total"], 2)
                else:
                    before = self._snapshot(fixture["wiki"])
                    with self.assertRaisesRegex(
                        materializer.MaterializationError, expected
                    ):
                        self._materialize(fixture)
                    self.assertEqual(before, self._snapshot(fixture["wiki"]))
                    self.assertFalse(fixture["receipt"].exists())

    def test_full_quote_copy_and_external_link_fail_before_write(self) -> None:
        for mode, message in (("quote", "full quote"), ("external", "external")):
            with self.subTest(message=message), tempfile.TemporaryDirectory() as temp_dir:
                fixture = self._fixture(Path(temp_dir))
                before = self._snapshot(fixture["wiki"])
                value = copy.deepcopy(fixture["changeset_value"])
                if mode == "quote":
                    first_record = json.loads(
                        fixture["evidence"].read_text(encoding="utf-8").splitlines()[0]
                    )
                    suffix = "\n" + first_record["quote"] + "\n"
                else:
                    suffix = "\n[external](https://example.com)\n"
                content = value["operations"][0]["proposed_content"] + suffix
                value["operations"][0]["proposed_content"] = content
                value["operations"][0]["proposed_sha256"] = _sha(content.encode("utf-8"))
                raw = _json_bytes(value)
                fixture["changeset"].write_bytes(raw)
                fixture["accepted_sha"] = _sha(raw)
                with self.assertRaisesRegex(materializer.MaterializationError, message):
                    self._materialize(fixture)
                self.assertEqual(before, self._snapshot(fixture["wiki"]))

    def test_symlink_component_and_existing_receipt_fail_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = self._fixture(Path(temp_dir))
            before = self._snapshot(fixture["wiki"])
            actual_batch = fixture["changeset"].parent
            linked_batch = fixture["repo"] / "linked-batch"
            linked_batch.symlink_to(actual_batch, target_is_directory=True)
            fixture["changeset"] = linked_batch / "changeset.json"
            with self.assertRaisesRegex(
                materializer.MaterializationError, "symlink component"
            ):
                self._materialize(fixture)
            self.assertEqual(before, self._snapshot(fixture["wiki"]))
            self.assertFalse(fixture["receipt"].exists())

        with tempfile.TemporaryDirectory() as temp_dir:
            fixture = self._fixture(Path(temp_dir))
            before = self._snapshot(fixture["wiki"])
            fixture["receipt"].write_text("already-owned\n", encoding="utf-8")
            with self.assertRaisesRegex(
                materializer.MaterializationError, "receipt target already exists"
            ):
                self._materialize(fixture)
            self.assertEqual(before, self._snapshot(fixture["wiki"]))
            self.assertEqual(
                fixture["receipt"].read_text(encoding="utf-8"), "already-owned\n"
            )


if __name__ == "__main__":
    unittest.main()
