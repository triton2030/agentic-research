"""Ranking-quality regression for `repeated-concepts`.

The contract/parity tests tolerate a cold index and only check output shape,
so they never caught the ranking bug: a degenerate transitive blob (one giant
connected component, many files bridged at near-zero cohesion) ranked #1 on
raw `unique_files`, burying the tight duplicates that matter for dedup. These
hermetic unit tests lock the cohesion-weighted ranking — no index, no network.
"""

from __future__ import annotations

from navigator.repeated_concepts import _concept_rank_score, _concept_sort_key


def _concept(unique_files: int, section_count: int, mean_cohesion: float, label: str = "x"):
    """Minimal concept dict — only the fields the ranking reads."""
    return {
        "unique_files": unique_files,
        "section_count": section_count,
        "mean_cohesion": mean_cohesion,
        "label": label,
    }


def test_rank_score_is_cohesion_times_sqrt_files() -> None:
    # Signal = mean_cohesion * sqrt(unique_files): cohesion gates, breadth is
    # sqrt-damped so it cannot dominate on its own.
    assert _concept_rank_score(_concept(4, 4, 0.142)) == 0.142 * (4 ** 0.5)
    assert _concept_rank_score(_concept(1, 1, 0.5)) == 0.5


def test_degenerate_blob_scores_below_tight_duplicate() -> None:
    # The bug: a 146-file component bridged at cohesion 0.006 used to rank #1.
    # It must now score far below a tight 2-file duplicate (real MAVO numbers).
    blob = _concept(146, 1115, 0.006, "mega-blob")
    tight = _concept(2, 2, 0.835, "tight-duplicate")
    assert _concept_rank_score(tight) > _concept_rank_score(blob)
    assert _concept_rank_score(blob) < 0.1  # effectively noise


def test_sort_surfaces_tight_duplicates_and_sinks_the_blob() -> None:
    # Reproduces the real MAVO top-6 before the fix, asserts the after order.
    items = [
        _concept(146, 1115, 0.006, "blob"),
        _concept(3, 23, 0.293, "mid"),
        _concept(2, 2, 0.835, "tight"),
        _concept(2, 4, 0.573, "tight2"),
    ]
    items.sort(key=_concept_sort_key)
    assert items[0]["label"] == "tight"   # highest cohesion-weighted score
    assert items[-1]["label"] == "blob"   # degenerate component sinks


def test_breadth_still_breaks_ties_at_comparable_cohesion() -> None:
    # unique_files is not ignored: at comparable cohesion the broader smear is
    # the stronger owner-truth signal and ranks first.
    items = [_concept(2, 4, 0.40, "narrow"), _concept(5, 10, 0.40, "broad")]
    items.sort(key=_concept_sort_key)
    assert items[0]["label"] == "broad"
