---
name: 1work-artifacts
description: Use when work leaves files outside canon (drafts, orchestration, Codex runs, images, debates) and needs a work folder, joins or ends one, or meets work folders left stale.
---

# Work artifacts

## Context

The owner keeps a work-artifacts folder in many projects and reads it to decide what moves to canon, so a folder leaves for the archive only with the owner's permission.
One piece of work is one folder holding what it leaves outside canon: drafts, probes, orchestration state, Codex runs, generated images, design debates.
Skills that write such files put them inside the folder of the work they serve, so the work and its trail are found and archived together.

Folders pile up faster than they close.
A session that meets an old folder cannot tell whether its work is finished, who did it or what is still open; the owner then has to remember it, and the next agent reads a stale draft as a decision not yet taken.
A folder can answer for itself when it says which sessions worked in it and where they run.
A session id alone is not enough: any agent, Claude or Codex, can message a session running in T3 by its T3 thread, which Codex there does not get in its environment, while a live Claude session outside T3 is reachable only from Claude.

## Task

Give each piece of work one folder that tells the owner what the work is and where it stands, and tells any session who worked on it and how to reach them.
When your work ends, ask the owner about archiving; when you meet stale folders, ask their live sessions and bring the owner one list, not one question per folder.

## Goal

Each work folder explains itself to the owner and to any session without anyone's memory, and leaves only by the owner's decision: the owner's choice about a folder outranks a tidy work-artifacts folder.

## When your work needs a place for files

A work folder is for files a piece of work leaves outside canon.
A session whose only output is commits, canon edits or a chat answer makes none: an empty folder is one more for the owner to close.
Files another skill keeps in its own project-wide place, such as HTML pages, handoffs, plans, findings or quotes, stay there, and the README says where they are.

Join the folder the work already has, if the owner, your task file or the orchestrator that briefed you names one.
Otherwise create one in the project's work-artifacts folder, which the project's instructions name; read that folder's `AGENTS.md`, because the project's rules for names, language, layout and archive win over this skill.
Where the project names none, use `_workspace/work-artifacts/`, creating it, and say so in your reply.
Name the folder `YYYY-MM-DD-<topic>`: the day the work starts and a topic in the owner's words and language, which no other folder has.

## When you create or join the folder

- `README.md` is the owner's entry, in plain words: what the work is, where it stands, the next step and what lies where. Keep it current as the work moves: the owner and the next session read it first.
- Files written for the owner sit at the top; agents' working material, such as briefs, orchestration and Codex runs, goes under `agents/`, so the owner can tell at once which files to read.
- Add your session's line to `agents/sessions.md` with this skill's script:

  ```bash
  python3 <this skill>/scripts/session_line.py <folder> --agent <claude or codex> --model <model> --does "<what you do here>"
  ```

  It reads the session ids from the environment, finds the T3 thread of a Codex session in T3's records, and leaves out a T3 thread id inherited from a parent session, which would send messages meant for you to that parent.
  If it reports no T3 thread for a Codex session that runs in T3, run it again with `--t3-thread <id>` when your brief or the session that launched you named your thread, and otherwise say in your reply that Claude sessions cannot reach you.
  Every session that works in the folder adds its own line, an executor in its own T3 thread or Codex run included; an executor of another agent family, such as Muse or Cursor, gets its line by hand from the session that launched it, with the T3 thread from the launch.
  An in-process subagent adds none: it ends with your turn, and you answer for it.

## When your work in the folder ends

Bring what is decided to canon by the project's route, write the outcome and what stays open in the README, and in the same turn ask the owner whether the folder may go to the archive.
With permission, move it to the project's archive folder (where the project names none, `_artifacts_archive/` inside the work-artifacts folder), re-point the links that led to it, and leave in it a reason file (the project's name for it, otherwise `Причина архивации.md`): why the work ended and what shows it, the owner's permission, where the open items went.
Archived folders are not rewritten to newer rules.

## When you meet stale folders

You see them when you list the work-artifacts folder.
A dated work folder, not the archive folder, is stale when no file in it but `agents/sessions.md` changed for a week, committed or not, ignored Codex runs included: `fd -HI -1 -t f --changed-within 1w -E sessions.md -E .DS_Store . <folder>` prints nothing.
A stale folder may be finished, abandoned or waiting for the owner, and only its README and its sessions can tell which.

1. Skip a folder whose `agents/sessions.md` has a `listed for the owner's archive decision` line from the last week, or a `kept by the owner` line with no file changed after it.
2. Mark each remaining folder before reading it, so a parallel session does not list it again: `session_line.py <folder> --agent <claude or codex> --model <model> --listed`.
3. Read its README and `agents/sessions.md`, and message each live session listed there by the routes in [reaching a session](references/reach-a-session.md): ask it to write in the README whether the work is finished and what is open. Do not wait for replies; reread the READMEs before you answer. A closed session is not resumed for this: a resume is a paid run, and the README and git history answer for it.
4. In your reply, bring the owner one list: each folder, its last change, what its README says, whom you asked and whether they answered, and your suggestion: archive, keep, or move the open items first. Archive the folders the owner permits, as above; for a folder the owner keeps, record it with `session_line.py <folder> … --kept "<the owner's reason>"`.
