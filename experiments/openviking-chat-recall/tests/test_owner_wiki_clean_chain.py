from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
REPO = EXPERIMENT.parents[1]
SCRIPT_DIR = EXPERIMENT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import build_owner_wiki_batch as builder  # noqa: E402
import materialize_chronological_changeset as materializer  # noqa: E402


FROZEN = EXPERIMENT / "artifacts/full-build/frozen/source-manifest.json"
EVIDENCE = EXPERIMENT / "artifacts/full-build/evidence/records.jsonl"
PROMPT = EXPERIMENT / "prompts/wiki-writer.v1.md"
MATERIALIZER = EXPERIMENT / "scripts/materialize_chronological_changeset.py"
EVIDENCE_COMMIT = "ea569e2bf84377b17be9177065d5fb9172d26d39"


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


class OwnerWikiCleanChainTests(unittest.TestCase):
    def _build_fixture(self, root: Path) -> dict[str, Path | dict]:
        wiki = root / "current/wiki"
        manifest_path = root / "batch-001-input.json"
        batch = root / "batch-001"
        changeset_path = batch / "changeset.json"
        preflight_path = batch / "preflight.json"
        receipt_path = batch / "receipt.json"
        wiki.mkdir(parents=True)

        manifest, preflight = builder.build_batch(
            repo_root=REPO,
            batch_number=1,
            frozen_manifest_path=FROZEN,
            evidence_records_path=EVIDENCE,
            evidence_commit=EVIDENCE_COMMIT,
            prompt_path=PROMPT,
            materializer_path=MATERIALIZER,
            wiki_root=wiki,
            manifest_path=manifest_path,
            changeset_path=changeset_path,
            preflight_path=preflight_path,
        )
        manifest_path.write_bytes(_json_bytes(manifest))
        preflight_path.parent.mkdir(parents=True)
        preflight_path.write_bytes(_json_bytes(preflight))

        record_ids = [item["record_id"] for item in manifest["record_bindings"]]
        source_links = "\n".join(
            f"- [Владелец высказался об общем предмете]({item['source_link_target']})"
            for item in manifest["record_bindings"]
        )
        question = "Что владелец сказал в первой хронологической группе?"
        page = (
            "---\n"
            "type: concept\n"
            f"title: {question}\n"
            "description: Высказывания владельца из первой группы.\n"
            "---\n\n"
            f"# {question}\n\n"
            "Владелец сформулировал несколько позиций в первой группе.\n\n"
            "## Источники\n\n"
            f"{source_links}\n"
        )
        index = (
            "---\n"
            "type: index\n"
            "title: Что говорил владелец?\n"
            "description: Навигация по высказываниям владельца.\n"
            "---\n\n"
            "# Что говорил владелец?\n\n"
            "Здесь собраны актуальные знания, пересказанные из слов владельца.\n\n"
            "## Первая группа\n\n"
            f"- [{question}](concept/first-group.md)\n"
        )
        manifest_raw = manifest_path.read_bytes()
        contract_sha = manifest["output"]["output_contract_sha256"]
        changeset = {
            "schema": builder.CHANGESET_SCHEMA,
            "phase": "semantic-draft",
            "status": "candidate",
            "batch_id": "batch-001",
            "previous_batch_id": None,
            "model": "gpt-5.6-luna",
            "thinking": "max",
            "input": {
                "manifest_path": manifest_path.relative_to(REPO).as_posix(),
                "manifest_sha256": _sha(manifest_raw),
                "evidence_records_path": EVIDENCE.relative_to(REPO).as_posix(),
                "evidence_records_sha256": manifest["evidence_records_sha256"],
                "corpus_commit": manifest["corpus_commit"],
                "evidence_commit": manifest["evidence_commit"],
                "time_boundary_utc": manifest["time_boundary_utc"],
                "prompt_path": manifest["prompt"]["path"],
                "prompt_sha256": manifest["prompt"]["sha256"],
                "materializer_path": manifest["materializer"]["path"],
                "materializer_sha256": manifest["materializer"]["sha256"],
                "output_contract_sha256": contract_sha,
            },
            "prior_checkpoint": manifest["prior_checkpoint"],
            "allowed_operations": manifest["output"]["output_contract"][
                "fixed_values"
            ]["allowed_operations"],
            "frozen_record_ids_in_manifest_order": record_ids,
            "operations": [
                {
                    "operation": "create",
                    "page_path": "current/wiki/concept/first-group.md",
                    "page_type": "concept",
                    "prior_sha256": None,
                    "proposed_content": page,
                    "proposed_sha256": _sha(page.encode("utf-8")),
                    "record_ids": record_ids,
                    "material_claims": [
                        {
                            "claim_id": "first-group",
                            "statement": "Владелец сформулировал позиции.",
                            "epistemic_kind": "source-backed",
                            "supporting_record_ids": record_ids,
                            "page_fit": {
                                "page_question": question,
                                "answering_record_ids": [record_ids[0]],
                                "reason": "Запись относится к первой группе.",
                            },
                        }
                    ],
                    "prior_page_review": {"checked_prior_pages": []},
                },
                {
                    "operation": "create",
                    "page_path": "current/wiki/index.md",
                    "page_type": "index",
                    "prior_sha256": None,
                    "proposed_content": index,
                    "proposed_sha256": _sha(index.encode("utf-8")),
                    "record_ids": [],
                    "material_claims": [],
                    "prior_page_review": {"checked_prior_pages": []},
                },
            ],
            "coverage": [
                {
                    "record_id": record_id,
                    "disposition": "used",
                    "page_path": "current/wiki/concept/first-group.md",
                    "reason": "Поддерживает claim first-group.",
                }
                for record_id in record_ids
            ],
            "evidence_metadata": {
                "repetition_groups": [],
                "unresolved_conflicts": [],
            },
            "gaps": [],
        }
        changeset_path.write_bytes(_json_bytes(changeset))
        return {
            "wiki": wiki,
            "manifest": manifest_path,
            "changeset": changeset_path,
            "receipt": receipt_path,
            "changeset_value": changeset,
        }

    def test_clean_batch_builds_and_v5_candidate_preflights(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO) as temp_dir:
            fixture = self._build_fixture(Path(temp_dir))
            changeset_path = fixture["changeset"]
            receipt = materializer.materialize(
                repo_root=REPO,
                changeset_path=changeset_path,
                manifest_path=fixture["manifest"],
                evidence_records_path=EVIDENCE,
                wiki_root=fixture["wiki"],
                receipt_path=fixture["receipt"],
                accepted_changeset_sha256=_sha(changeset_path.read_bytes()),
                dry_run=True,
            )
            self.assertEqual(receipt["schema"], builder.RECEIPT_SCHEMA)
            self.assertEqual(receipt["batch_id"], "batch-001")
            self.assertEqual(receipt["active_page_set"]["count"], 2)
            self.assertEqual(
                receipt["source_snapshot"]["prompt_sha256"],
                _sha(PROMPT.read_bytes()),
            )

    def test_v5_wrong_prompt_echo_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO) as temp_dir:
            fixture = self._build_fixture(Path(temp_dir))
            changeset_path = fixture["changeset"]
            value = fixture["changeset_value"]
            value["input"]["prompt_sha256"] = "0" * 64
            changeset_path.write_bytes(_json_bytes(value))
            with self.assertRaisesRegex(
                materializer.MaterializationError, "prompt/output bindings"
            ):
                materializer.materialize(
                    repo_root=REPO,
                    changeset_path=changeset_path,
                    manifest_path=fixture["manifest"],
                    evidence_records_path=EVIDENCE,
                    wiki_root=fixture["wiki"],
                    receipt_path=fixture["receipt"],
                    accepted_changeset_sha256=_sha(changeset_path.read_bytes()),
                    dry_run=True,
                )


if __name__ == "__main__":
    unittest.main()
