# Opus candidate-v2 review

Model: claude-opus-5
Session: fe57aa49-de92-44a3-933a-513693eea101

**Verdict: conformant, with one remaining material item in the product frame and one delivery-integrity item.** No defect found in the runtime bodies themselves.

## Checked scope

Full bytes of all 17 files in `candidate-v2/{claude,codex}`, `diff -r` against `baseline/{claude,codex}` and against `candidate/` (v1), the claude↔codex delta per file, `intent-and-preservation.md`, `review-intent.md`, `review-requirements.md`, `state.md`, `candidate-sha256.json`, `boundary-probe-input.md` + `boundary-probe-output.md` (it has finished). Ran only read-only checks: frontmatter/link/YAML validation (all links resolve, all references carry frontmatter, YAML parses; the single 150-char line is the mode table row in `SKILL.md:50`), SHA-256 recomputation, and verification of every owner citation the candidate changed against `_ops/chat-recall`. I did not run the skill and did not treat either probe as a live panel run or as evidence of improved reliability.

## Prior findings — all five resolved in the bytes

- Four-native-report contract → `synthesis.md:7` now "три родных отчёта и Premortem", identical in both runtimes.
- No terminal for copied reports → `synthesis.md:18-22` plus `SKILL.md:52-59`; boundary case 4 produces `panel_incomplete` rather than a handback.
- Stale frame/FE-4 → TB1 (`product-frame.md:12-13`), TB5 (`:19-21`), Аппетит (`:23-26`), FE-4 note (`principles:41-42`), FE-1 application note, FE-8. Citation repair verified: baseline's `2026-08-10-…:14` is now an empty line, and the candidate's `:17` / `:20` resolve to the correct owner quotes; `2026-04-28-…:21-22` genuinely contains both «не есть самоцель» and «хорошую работу испортишь».
- Claude continuation mechanism → `named.md:9`, `panel.md:18`, `steering.md:13` retain the conversation ID; leaving resume unversioned is a reasonable call, not a gap.
- Sync/frame delivery → owner-ruled; not reopened.

Runtime drift surface also shrank: `SKILL.md`, `packet.md`, `synthesis.md` are byte-identical across runtimes and reference descriptions are runtime-neutral, so the one-sided-edit class that produced the synthesis defect is largely closed. The three v2 corrections and both reviewer findings (INT-1, R1, R2) are present in the actual bytes.

## Remaining material finding

**`candidate-v2/claude/product-frame.md:5-8` (Цель-сцена) is the only frame section not reconciled, and it contradicts the composition the rest of the file just fixed.** It still reads "зовёт панель заведомо разных линз **из ростера нативных критиков**". The adopted contract is a fixed composition whose fourth lens is neither native nor in the roster: TB5 in the same file (`:19-21`), FE-7 (`product-frame.principles.md:71-82`), and the owner quote at `references/panel.md:8-9`. Failure: the frame is what the next autonomous author reads as intent — this refactor spent a cycle undoing exactly that influence (`intent-and-preservation.md:76-77`) — and a scene licensing lens selection from a roster re-opens both roster substitution and the dropped cross-family fourth. Minimal correction: name the fixed set in that sentence ("фиксированную панель — `ladder`, `solvent`, `prospector` и Premortem другой модельной семьи"), leaving the rest of the scene as is. Prediction, not an observed failure.

## Delivery integrity

**`candidate-sha256.json` and `state.md:18` both point at the superseded v1 directory.** Recomputed hashes: `claude/SKILL.md`, `codex/SKILL.md`, both `packet.md` and both `panel.md` mismatch the json (the json matches `candidate/`, v1); the other 12 entries match. `state.md:18` still says "Кандидат в `candidate/`" while `:30` plans "доставку явного runtime manifest". Failure: installing or verifying against the recorded fingerprint ships the pre-correction bytes — precisely the files carrying the unread-zone preference, the external-changes wording, and the technical-block/`uncertain` distinction. Minimal correction: point `state.md` at `candidate-v2/` and regenerate the hash file for those bytes before delivery. Note also that the "exclude the frame pair from runtime delivery" decision currently exists only as prose (`intent-and-preservation.md:85`); no manifest artifact exists in `candidate-v2`, so installation has to be driven by an explicit file list.

## Non-blocking observations

- `SKILL.md:56` names `rung_missing` — vocabulary owned by the `ladder` definition; it works as an example but couples the body to a role's verdict names the frame says belong to definitions.
- `panel.md:15` re-introduces "параллельно", which was cut on 2026-08-11 as a harness default (`skills/1fresh-eyes/cut.md:41`); harmless and arguably clearer, but it is a reversal not recorded in the preservation map.

## Limits

Text-and-bytes review only; every behavioral statement above is a prediction. Simulation outputs were read for conformance of stated decisions to the new text, not as panel runs or as evidence of improvement. Role definitions and the sync-helper question were out of scope and not re-examined.

