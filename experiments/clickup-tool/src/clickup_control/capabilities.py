from __future__ import annotations

CAPABILITY_MAP: dict[str, list[str]] = {
    "work_model": [
        "Tasks and subtasks for accountable work with independent lifecycle",
        "Docs/Wikis for narrative knowledge and Goals/Targets for outcomes",
        "Views and Dashboards for lenses/reporting without duplicating work",
        "Forms for intake, Automations for repeated reactions, Whiteboards for ideation",
        "Custom task types, fields, relationships, and dependencies for structure",
    ],
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
