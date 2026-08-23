#!/usr/bin/env python3
"""Стадия 1 для любой папки реплик: один разговор — один агент.

Первый прогон этой стадии был разовым и в скриптах не остался, поэтому проверить
переносимость протокола было нечем. Здесь она собирается из того же контракта
`flatten-file.v1.md` и работает над любой папкой — в том числе чужого проекта.

Агент ничего не читает и ничего не пишет: разговор приходит в брифе, ответ
кладёт на место скрипт. Так требует инвариант 2 протокола.

    python3 build_flatten_tasks.py <папка реплик> <папка заданий>
"""
from __future__ import annotations

import glob
import os
import sys

CONTRACT = "experiments/openviking-chat-recall/prompts/flatten-file.v1.md"


def main(corpus: str, out_dir: str) -> int:
    contract = open(CONTRACT, encoding="utf-8").read()
    os.makedirs(out_dir, exist_ok=True)
    written = 0
    for path in sorted(glob.glob(os.path.join(corpus, "*.md"))):
        name = os.path.basename(path)
        if name == "README.md":
            continue
        numbered = "\n".join(
            f"{i}: {line.rstrip()}"
            for i, line in enumerate(open(path, encoding="utf-8"), start=1)
        )
        open(os.path.join(out_dir, name[:-3] + ".txt"), "w", encoding="utf-8").write(
            f"""Роль: редактор, превращающий запись разговора в сухое знание. Ниже контракт
работы, затем сам разговор с пронумерованными строками.

{contract}

## Разговор `{name}`

Номер перед двоеточием — номер строки. Именно его ставь в `[L<строка>]`.

```
{numbered}
```

## Ответ

Верни **только содержимое выходного файла** — от `---` до последнего пункта.
Ни пояснений вокруг, ни markdown-обёртки, ни файлов на диске: положить результат
на место — не твоя работа.
""")
        written += 1
    print(f"заданий стадии 1: {written} -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
