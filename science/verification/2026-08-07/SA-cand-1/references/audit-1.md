# Deep audit 1


Rare mode: full audit of a skill/runtime/control-surface landscape, not design
or repair of one skill. Use this when the user asks for a broad audit or when
the system keeps adding surfaces without a clear owner.

## Eight Steps

Keep the order. Current-state map and forces come before failure scan.

### 1. Telos

Read the live owner docs that constrain the audit: root/local instructions,
goal/README/task files if present, and the user's current request.

Done when goal, scope, stop rule, and constraining owners are explicit. If the
upstream layer is missing or stale, report that instead of compensating with
general architecture.

### 2. As-is Map

Inventory actual capabilities before diagnosing failures:

- skills and their trigger boundaries;
- agents and tool policies;
- hooks, permissions, validators, lifecycle rules;
- instruction layers and precedence;
- scripts or commands that already enforce behavior;
- mismatches between text and reality.

Use exact handles, not classes. "Hook exists" is too vague; name event, matcher,
and action.

### 3. Forces

Name 2-3 current design constraints that could age the recommendation: model
shift, tool-surface change, repo growth, new task class, owner change.

Each force needs an early signal and a design constraint. Generic future change
without a signal is out of scope.

### 4. Failure Classes

Group concrete failures by root cause. Tie each failure to a place the current
system permits it and to an existing surface that should have covered it but
does not.

Done when failures are classes, not a flat patch list.

### 5. Leverage

Prefer one intervention that removes a class over several one-off patches.

- `high`: covers 3+ failures;
- `medium`: covers 2;
- `low`: covers 1.

Do not recommend a new surface until reuse-first has failed.
