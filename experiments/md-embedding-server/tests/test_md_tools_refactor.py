from __future__ import annotations

from argparse import Namespace

from navigator.folder_map import build_map
from navigator.importance import importance_rows
from navigator.related import collect_related_items
from navigator.section_profile import classify_section, classify_section_llm


def test_build_map_with_link_counts(tmp_path):
    root = tmp_path / "corpus"
    root.mkdir()
    (root / "a.md").write_text("# A\n\nSee [B](b.md).\n", encoding="utf-8")
    (root / "b.md").write_text("# B\n\n", encoding="utf-8")

    data = build_map(root, max_heading_level=2, with_link_counts=True)
    by_rel = {item["relative_path"]: item for item in data["files"]}

    assert by_rel["a.md"]["out_degree"] == 1
    assert by_rel["b.md"]["in_degree"] == 1


def test_importance_rows_rank_link_target(tmp_path):
    root = tmp_path / "corpus"
    root.mkdir()
    (root / "a.md").write_text("# A\n\n[[b]]\n", encoding="utf-8")
    (root / "b.md").write_text("# B\n\n", encoding="utf-8")

    rows = importance_rows(root, top=2, sort_by="in_degree")

    assert rows[0]["relative_path"] == "b.md"
    assert rows[0]["in_degree"] == 1
    assert "centrality" in rows[0]


def test_read_related_preview_omits_content(tmp_path):
    root = tmp_path / "corpus"
    root.mkdir()
    anchor = root / "a.md"
    anchor.write_text("# A\n\nSee [B](b.md).\n", encoding="utf-8")
    (root / "b.md").write_text("# B\n\nBody.\n", encoding="utf-8")

    packet = collect_related_items(
        Namespace(
            paths=[str(anchor)],
            scan=str(root),
            include="self,markdown-links",
            token_budget=0,
            semantic_radius=0,
            check_links=False,
            link_distance_threshold=0.4,
            anchor_aware=True,
            mode="preview",
        )
    )

    assert packet["items"]
    assert all("content" not in item for item in packet["items"])
    assert all("headings" in item for item in packet["items"])


def test_read_related_semantic_status_reports_missing_index(tmp_path):
    root = tmp_path / "corpus"
    root.mkdir()
    anchor = root / "a.md"
    anchor.write_text("# A\n\nSee [B](b.md).\n", encoding="utf-8")
    (root / "b.md").write_text("# B\n\nBody.\n", encoding="utf-8")

    packet = collect_related_items(
        Namespace(
            paths=[str(anchor)],
            scan=str(root),
            include="self,markdown-links",
            token_budget=0,
            semantic_radius=2,
            check_links=False,
            link_distance_threshold=0.4,
            anchor_aware=True,
            mode="preview",
        )
    )

    assert packet["semantic_status"] == "no_index"
    assert packet["semantic_neighbors"] == []


def test_section_profile_classifies_rule_and_question():
    rule = classify_section(
        {
            "heading_text": "Runtime Rule",
            "heading_chain": "Runtime Rule",
            "body": "Always verify evidence. Never claim done without tests.",
        }
    )
    question = classify_section(
        {
            "heading_text": "Open questions",
            "heading_chain": "Open questions",
            "body": "TODO: should this become a separate owner file?",
        }
    )

    assert rule["type"] == "rule"
    assert question["type"] == "open-question"


def test_section_profile_llm_strips_extra_json_tail():
    class Client:
        def completion(self, **kwargs):
            return '{"type":"rule","subject":"S","owns_terms":["x"],"mentions":[],"evidence_sources":[],"confidence":0.9}\nextra'

    profile = classify_section_llm(
        {"heading_text": "H", "heading_chain": "H", "body": "Always do X."},
        client=Client(),
        model="test-model",
    )

    assert profile["type"] == "rule"
    assert profile["confidence"] == 0.9
