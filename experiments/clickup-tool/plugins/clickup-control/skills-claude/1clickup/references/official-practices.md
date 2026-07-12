# Official ClickUp Practices

Snapshot: 2026-07-12. These are condensed from current ClickUp Help guidance;
follow the links when plan limits or recent product behavior matter.

## Hierarchy And Projects

- ClickUp recommends one Workspace per organization and commonly one Space per
  team/department or distinct workflow.
- Match project size to hierarchy depth: Task in a List for small work, List in
  a Folder for medium projects, Folder with stage/team Lists for large projects.
- Use Tasks in Multiple Lists when the same work belongs in another portfolio or
  reporting location; avoid copying the task and splitting truth.
- Keep permissions and shared/private boundaries at the highest sensible
  hierarchy level.

Sources: [Hierarchy basics](https://help.clickup.com/hc/en-us/articles/13856392825367-Intro-to-the-Hierarchy),
[Hierarchy best practices](https://help.clickup.com/hc/en-us/articles/20480724378135-Hierarchy-best-practices),
[project hierarchy](https://help.clickup.com/hc/en-us/articles/9703037723159-Organize-your-Hierarchy-for-project-management).

## Tasks, Types, Fields, And Relationships

- Use subtasks when child work needs its own fields/lifecycle. Use checklists for
  quick grouped to-dos; convert checklist items when they grow into real work.
- Use custom task types for durable business entities such as Bug, Campaign,
  Invoice, Account, or Project. Set List defaults and use types in filters,
  templates, and Automations.
- Use type-scoped Custom Fields when metadata follows the entity type; use
  location-scoped fields when metadata follows where work lives.
- Use dependencies for blocking/sequencing. Use Custom Relationships for
  semantic connections and List-to-List rollups.

Sources: [tasks](https://help.clickup.com/hc/en-us/articles/10552031987735-Intro-to-tasks),
[subtasks](https://help.clickup.com/hc/en-us/articles/6309825777943-Intro-to-subtasks),
[checklists](https://help.clickup.com/hc/en-us/articles/6309942197783-Use-task-checklists),
[custom task types](https://help.clickup.com/hc/en-us/articles/17564381376919-Custom-task-types),
[fields by type](https://help.clickup.com/hc/en-us/articles/30976239926167-Intro-to-Custom-Fields-by-task-type),
[relationships](https://help.clickup.com/hc/en-us/articles/6309153663639-Custom-Relationships).

## Views And Reporting

- List is the primary flexible view for grouping, sorting, filtering, columns,
  and bulk edits; Board is for workflow/Kanban; Gantt for sequencing and
  dependencies; Calendar for dated work; Timeline for roadmaps; Workload/Team
  for capacity; Table for dense analysis; Map for location data.
- Create another View of the same work instead of duplicating data. Name Views
  by purpose, pin important ones, set sensible defaults, and protect shared
  reporting views when needed.
- Use Dashboards for high-level metrics, trends, time, and project performance.
  Refresh/auto-refresh and check card filters before treating a dashboard as
  current evidence.

Sources: [views](https://help.clickup.com/hc/en-us/articles/6329880717719-Intro-to-views),
[view practices](https://help.clickup.com/hc/en-us/articles/20480724378135-Hierarchy-best-practices),
[Dashboards](https://help.clickup.com/hc/en-us/articles/6312197753239-Intro-to-Dashboards).

## Knowledge, Strategy, Intake, And Ideation

- Use Docs for collaborative narrative; promote durable sources of truth to
  Wikis. Link Docs and tasks instead of duplicating requirements.
- Use Goals for high-level measurable outcomes and Targets for number,
  currency, true/false, or task/List completion. Combine Goals with Docs for
  context, List/Gantt views for execution, and Dashboards for executive tracking.
- Use Forms for structured feedback, requests, applications, orders, or intake;
  submissions become tasks and can apply templates/assignment. Analyze intake
  with Dashboards rather than manually summarizing every submission.
- Use Whiteboards for brainstorming, flowcharts, and workshops, then convert
  stabilized shapes/notes into tasks or Docs.

Sources: [Docs](https://help.clickup.com/hc/en-us/articles/6328174371351-Intro-to-Docs),
[Goals and OKRs](https://help.clickup.com/hc/en-us/articles/6327987972119-Use-ClickUp-to-track-goals-and-OKRs),
[Forms](https://help.clickup.com/hc/en-us/articles/6310233090711-Intro-to-Forms-and-Form-view),
[Whiteboards](https://help.clickup.com/hc/en-us/articles/6326615000471-Intro-to-Whiteboards).

## Automation

- Automate repeated task-related busywork with Trigger → optional Conditions →
  one or more Actions. Prefer a named, observable rule over hidden manual habit.
- Apply templates, assignments, fields, messages, emails, or moves only after
  validating the target location and permissions.
- Check Automation Activity and plan action limits; subtasks/nested subtasks and
  Move-to-List actions have special propagation behavior.

Source: [Create an Automation](https://help.clickup.com/hc/en-us/articles/30241682127127-Create-an-Automation).
