# ClickUp Work Model

Use this model before creating anything. Choose the object that matches the
meaning of the work; do not turn every noun, note, metric, or idea into a Task.

## Object Selection

| User outcome | Prefer | Use when | Do not substitute with |
|---|---|---|---|
| Accountable action | Task | One work item needs status, owner, priority, dates, discussion, or audit trail | A Doc paragraph or checklist item |
| Independently managed part of a task | Subtask | The part needs its own assignee, dates, priority, status, or details | A lightweight checklist item |
| Small steps inside one task | Checklist | Steps share the parent lifecycle and need little independent metadata | Dozens of fake subtasks |
| Durable narrative or source of truth | Doc; Wiki when canonical | Requirements, decisions, procedures, research, meeting notes, or knowledge must be read and revised | An oversized task description |
| Measurable outcome | Goal + Targets/KRs | Progress is numeric, currency, true/false, or linked to task/List completion | A vague "goal" task |
| Same work, different lens | View | Users need grouping, filtering, scheduling, capacity, maps, or workflow visualization | Duplicate Lists or copied tasks |
| Incoming request/data capture | Form | External or internal respondents should submit structured information that becomes a task | Manually creating every intake task |
| Repeated deterministic reaction | Automation | A trigger plus optional conditions should apply templates, fields, assignments, messages, or moves | Repeating the same manual edits |
| Aggregate measurement/report | Dashboard | Leaders or clients need high-level metrics, trends, time, or project performance | A reporting task or static status Doc alone |
| Spatial ideation and collaboration | Whiteboard | Brainstorming, flowcharts, workshops, or early planning benefits from a shared canvas | Premature tasks before ideas stabilize |
| Business entity with distinct semantics | Custom task type | Bugs, campaigns, invoices, accounts, projects, or milestones need type-specific fields and behavior | Name prefixes like `[BUG]` everywhere |
| Reusable metadata | Custom Field | Work must be filtered, grouped, calculated, automated, reported, or collected by Form | Tags for structured values |
| Lightweight categorization | Tag | A flexible cross-location label is enough and no schema is required | A Custom Field with no real structure |
| Blocking or sequencing | Dependency | One task cannot start/finish before another | A comment saying "blocked" |
| Semantic association | Relationship | Entities are related but neither blocks the other; List relationships can support rollups | Dependency or duplicate task |
| Actual effort and forecast | Time estimate + time tracking | Capacity, billing, variance, or delivery learning matters | Status timestamps alone |
| Conversation about a work item | Task/Doc comment; Chat for channel discussion | Context should remain near its object or team channel | A new task whose only purpose is a message |

## Hierarchy Selection

- Workspace: one organization and its work; avoid parallel Workspaces without a
  real isolation boundary.
- Space: team, department, high-level initiative, client domain, or distinct
  workflow with shared settings.
- Folder/Subfolder: portfolio, large/cross-functional project, or grouped Lists.
- List: a coherent project, process, phase, backlog, or dataset of work items.
- Task/Subtask: actionable units inside that structure.

Official sizing heuristic:

- small project: one List, project represented by a Task; use subtasks for
  contributors;
- medium project: project represented by a List inside a Folder;
- large project: project represented by a Folder with Lists/Subfolders for
  stages or teams.

## Decision Checks

Before creating an object, ask:

1. Is this an action, knowledge, outcome, lens, intake, rule, metric, or idea?
2. Does it need an independent lifecycle, owner, dates, permissions, or schema?
3. Does the object already exist and only need another View, Relationship, or
   List membership?
4. Will this structure reduce recurring manual work, or merely add another
   container?
5. Which ClickApp, plan, role, and API/UI limitations apply?
