"""One-off fresh-process checks of the installed native Expansionist profiles."""

from pathlib import Path
import datetime
import json
import subprocess
import sys
import tempfile

work = Path(__file__).resolve().parent
runtime = sys.argv[1]
out = work / f"native-{runtime}"
out.mkdir(exist_ok=True)
cwd = Path(tempfile.mkdtemp(prefix=f"fresh-eyes-{runtime}-"))

if runtime == "codex":
    prompt = (
        "Это ограниченная проверка установленного скилла. Примени установленный "
        "1fresh-eyes в режиме named: пользователь явно выбирает только профиль "
        "expansionist. Прочти пакет " + str(work / "probes/opportunity.md") + ". "
        "Запусти ровно одного настоящего субагента типа expansionist в свежем "
        "окне без наследования истории и дождись его конечного отчёта. "
        "Не заменяй отсутствующий профиль обычным агентом и не воспроизводи "
        "его инструкцию вручную. Если native-профиль недоступен, сообщи этот факт. "
        "Не меняй файлы и не запускай полную панель. В финале верни ID запущенного "
        "агента и его отчёт, сохранив вердикт и основания."
    )
    argv = [
        "codex", "exec", "--ephemeral", "--json", "--color", "never",
        "-s", "read-only", "-C", str(cwd), "--skip-git-repo-check",
        "-o", str(out / "output.md"), "-",
    ]
elif runtime == "claude":
    prompt = (
        "Прочти пакет " + str(work / "probes/boundary.md") + " и выполни свою "
        "роль Expansionist для указанного вопроса. Это ограниченная проверка "
        "установленного native-профиля на синтетическом случае. Исследование "
        "и отчёт; файлы не меняй, других агентов не запускай."
    )
    argv = [
        "claude", "--agent", "expansionist", "--print", "--verbose",
        "--output-format", "stream-json", "--no-session-persistence",
        "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
    ]
else:
    raise ValueError(runtime)

(out / "input.md").write_text(prompt + "\n")
start = datetime.datetime.now(datetime.timezone.utc)
with (out / "events.jsonl").open("w") as stdout, (out / "stderr.txt").open("w") as stderr:
    result = subprocess.run(argv, input=prompt, text=True, cwd=cwd, stdout=stdout, stderr=stderr)
meta = {
    "runtime": runtime, "argv": argv, "cwd": str(cwd),
    "started_at": start.isoformat(),
    "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "exit_code": result.returncode,
}
(out / "run.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(meta, ensure_ascii=False))
if runtime == "claude":
    for line in (out / "events.jsonl").read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "result":
            (out / "output.md").write_text(event.get("result", "") + "\n")
            print(json.dumps({k: event.get(k) for k in ["subtype", "is_error", "session_id", "num_turns"]}, ensure_ascii=False))
print((out / "output.md").read_text() if (out / "output.md").exists() else "No final output file")
