from __future__ import annotations

from typing import Any

from .audit_severity import SEVERITY_CRITICAL, SEVERITY_INFO, SEVERITY_WARNING


def render_audit(out: dict[str, Any]) -> str:
    """Doctor's-report-style Markdown: severity-grouped sections, each
    finding with badge / label / evidence / next-step."""
    counts = out["severity_counts"]
    health = out["health"]
    if health >= 80:
        health_emoji = "🟢"
    elif health >= 50:
        health_emoji = "🟡"
    else:
        health_emoji = "🔴"

    lines = [
        f"# Markdown audit: {out['root']}",
        "",
        f"**Health: {health}/100** {health_emoji}  "
        f"(🔴 {counts['critical']} · 🟡 {counts['warning']} · ℹ️ {counts['info']})",
        "",
        f"Indexed: {out['stats']['files_indexed']} files / "
        f"{out['stats']['sections_indexed']} sections  "
        f"(engine: `{out['engine']['embed_model']}`)",
        "",
    ]

    findings = out.get("findings") or []
    if not findings:
        lines.append("_No findings above thresholds. Corpus looks structurally healthy._")
        lines.append("")
        return "\n".join(lines) + "\n"

    # Group by severity.
    by_sev: dict[str, list[dict[str, Any]]] = {
        SEVERITY_CRITICAL: [],
        SEVERITY_WARNING: [],
        SEVERITY_INFO: [],
    }
    for f in findings:
        by_sev[f["severity"]].append(f)

    sev_titles = {
        SEVERITY_CRITICAL: f"## 🔴 Critical ({len(by_sev[SEVERITY_CRITICAL])})",
        SEVERITY_WARNING: f"## 🟡 Warning ({len(by_sev[SEVERITY_WARNING])})",
        SEVERITY_INFO: f"## ℹ️ Info ({len(by_sev[SEVERITY_INFO])})",
    }

    for sev in (SEVERITY_CRITICAL, SEVERITY_WARNING, SEVERITY_INFO):
        bucket = by_sev[sev]
        if not bucket:
            continue
        lines.append(sev_titles[sev])
        lines.append("")
        for f in bucket:
            lines.append(f"### {f['class']} — {f['label']}")
            lines.append("")
            lines.extend(_render_evidence(f))
            lines.append("")
            lines.append(f"**Next step:** {f.get('next_step') or '_(no specific action)_'}")
            lines.append("")

    lines.append("## Thresholds")
    lines.append("")
    for k, v in out["thresholds"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines) + "\n"


def _render_evidence(f: dict[str, Any]) -> list[str]:
    """Class-specific evidence rendering. Keeps the report compact but
    surfaces the top items per finding."""
    ev = f.get("evidence") or {}
    out: list[str] = []
    cls = f["class"]

    if cls == "discovery_gaps":
        out.append(
            f"- Coverage gap: {ev['files_without_description']}/{ev['files_total']} files "
            f"({int(ev['gap_ratio'] * 100)}%)"
        )
        for path in ev.get("examples", []):
            out.append(f"  - `{path}`")

    elif cls == "smeared_owner_truth":
        rep = ev["representative"]
        out.append(
            f"- Across **{ev['unique_files']} files**, {ev['section_count']} sections, "
            f"cohesion {ev['cohesion']}"
        )
        out.append(f"- Representative: `{rep['relative_path']}` — {rep['heading_chain']}")
        for path in ev.get("files", [])[:4]:
            out.append(f"  - `{path}`")

    elif cls == "tight_duplicates":
        out.append(
            f"- Classification: **{ev['classification']}**, {ev['pair_count']} pair(s)"
        )
        for pair in ev.get("top_pairs", [])[:3]:
            out.append(
                f"  - sim {pair['similarity']}, heading-jaccard {pair['heading_jaccard']}  "
                f"`{pair['a']['relative_path']}` ↔ `{pair['b']['relative_path']}`"
            )

    elif cls == "intra_file_drift":
        for fdrift in ev.get("files", []):
            sources = fdrift.get("sources", [])
            src_tag = "+".join(s.replace("_", " ") for s in sources) or "?"
            line = (
                f"- `{fdrift['relative_path']}` — {fdrift['section_count']} sections "
                f"(via {src_tag})"
            )
            extras: list[str] = []
            if "tight_clusters" in fdrift:
                extras.append(
                    f"{fdrift['tight_clusters']} embed-clusters, "
                    f"inter-cluster sim {fdrift.get('inter_cluster_sim')}"
                )
            if "heading_diversity" in fdrift:
                extras.append(
                    f"heading-lex diversity {fdrift['heading_diversity']}"
                )
            if extras:
                line += "; " + "; ".join(extras)
            out.append(line)
            for g in fdrift.get("topic_groups", [])[:3]:
                if g.get("heading_chain"):
                    out.append(f"  - embed-cluster of {g['size']}: {g['heading_chain']}")
            for h in fdrift.get("headings_sample", [])[:4]:
                out.append(f"  - heading: {h}")

    elif cls == "template_family":
        out.append(
            f"- Shared H2+ heading `'{ev['shared_heading']}'` appears in "
            f"**{ev['file_count']} files**"
        )
        for path in ev.get("files", [])[:6]:
            out.append(f"  - `{path}`")

    elif cls == "cluster_folder_mismatch":
        out.append(
            f"- Cluster of {ev['cluster_size']} sections, cohesion {ev['cohesion']}, "
            f"no shared folder"
        )
        out.append(f"- Centroid: `{ev['centroid_path']}`")
        for top in ev.get("top_files", [])[:3]:
            out.append(f"  - `{top['path']}` ({top['section_count']} sections)")

    else:
        # Generic dump for unknown classes.
        out.append(f"- {ev}")

    return out


