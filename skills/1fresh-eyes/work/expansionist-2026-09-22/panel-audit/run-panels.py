"""Run two separate fresh Codex coordinators against the installed full panel."""

from pathlib import Path
import datetime
import hashlib
import json
import shutil
import subprocess
import tempfile

audit = Path(__file__).resolve().parent
manifest = {}
for path in sorted((audit / "cases").rglob("*.md")):
    manifest[str(path.relative_to(audit))] = hashlib.sha256(path.read_bytes()).hexdigest()
(audit / "case-sha256.json").write_text(json.dumps(manifest, indent=2) + "\n")

for name in ["pilot", "release"]:
    scratch = Path(tempfile.mkdtemp(prefix=f"fresh-panel-{name}-"))
    shutil.copytree(audit / "cases" / name, scratch / "case")
    (scratch / "reports").mkdir()
    out = audit / f"run-{name}"
    out.mkdir(exist_ok=True)
    prompt = (
        "Пользователь просит применить установленный 1fresh-eyes, полную панель, "
        "к вопросу в case/README.md. Все исходные факты вымышленного продуктового "
        "кейса находятся только в case/. Реши вопрос как в обычной работе по "
        "живому скиллу. Это выполнение панели, не рецензия на её инструкции. "
        "Роли выбирай из действительно доступных native-профилей; не имитируй "
        "отсутствующую роль и не переписывай методы вместо их вызова. "
        "Перед первым отчётом сохрани подготовленные пакеты в packets/. "
        "Сохрани каждый терминальный отчёт дословно в reports/, затем выполни "
        "предусмотренный скиллом синтез в synthesis.md. Рядом в run.json сохрани "
        "имена ролей, реальные ID, модель другой семьи, статус и время запусков "
        "и возвратов. Если проход неполон, сохрани точное препятствие. "
        "Исходные case/ и глобальные skills/agents не меняй. Допустимы исследование, "
        "сеть для чтения источников и запись результатов только в текущую "
        "временную папку. Критерии оценщика, другие кейсы, чужие отчёты и историю "
        "основной задачи не ищи. Никаких внешних изменений. В финале кратко верни "
        "решение и пути результатов."
    )
    (out / "input.md").write_text(prompt + "\n")
    argv = [
        "codex", "exec", "--json", "--color", "never", "-s", "workspace-write",
        "-C", str(scratch), "--skip-git-repo-check", "-o", str(out / "output.md"), "-",
    ]
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    launch = {"case": name, "cwd": str(scratch), "argv": argv, "started_at": start}
    (out / "launch.json").write_text(json.dumps(launch, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"started": name, "cwd": str(scratch)}, ensure_ascii=False), flush=True)
    with (out / "events.jsonl").open("w") as stdout, (out / "stderr.txt").open("w") as stderr:
        result = subprocess.run(argv, input=prompt, text=True, cwd=scratch, stdout=stdout, stderr=stderr)
    launch["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    launch["exit_code"] = result.returncode
    launch["case_unchanged"] = all(
        hashlib.sha256((scratch / "case" / p.relative_to(audit / "cases" / name)).read_bytes()).hexdigest()
        == hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (audit / "cases" / name).rglob("*.md")
    )
    (out / "launch.json").write_text(json.dumps(launch, ensure_ascii=False, indent=2) + "\n")
    for relative in ["packets", "reports", "run.json", "synthesis.md"]:
        source = scratch / relative
        if source.is_dir():
            shutil.copytree(source, out / relative)
        elif source.is_file():
            shutil.copy2(source, out / relative)
    print(json.dumps({"finished": name, "exit_code": result.returncode, "case_unchanged": launch["case_unchanged"]}, ensure_ascii=False), flush=True)
