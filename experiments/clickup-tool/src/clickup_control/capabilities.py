from __future__ import annotations

CAPABILITY_MAP: dict[str, list[str]] = {
    "official_mcp": [
        "semantic workspace search",
        "assignee resolution",
        "common task, Docs, Chat, and time composites",
    ],
    "public_api": [
        "hierarchy, tasks, fields, tags, checklists, links, dependencies",
        "comments, attachments, Docs, Views, Goals and Key Results",
        "time tracking, time in status, webhooks and templates",
        "experimental Chat v3 and plan-dependent administration",
        "generic v2/v3 endpoint access through guarded API operations",
    ],
    "desktop_fallback": [
        "Automations",
        "Dashboards",
        "Whiteboards",
        "workspace settings and other UI-only flows",
    ],
}
