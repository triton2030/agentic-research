# Broader Than Intent

## Observation

Когда user даёт задачу с topic-словом без жёстких границ («self-learning после хода»), модель по дефолту интерпретирует **шире**, чем user задумывал. Это требует второго (третьего) хода user'а на сужение.

Pattern: vague user spec → модель fills gaps максимально широко («процесс, инструкции, mechanisms, шероховатости») → user narrows down («только AI работа, граница с `1findings`»). Cost — extra turn и первая итерация инструкции выходит with looser boundaries, чем пользователь хотел.

Психологически: «чем шире — тем больше шансов попасть в intent» побеждает «уточни scope до того как пишешь». Это **safer-bet bias**, но не helpful-bet.

## Counter

- 2026-05-19 [Claude Opus 4.7]: Self-Learning слой в `1work-review`. User сказал «pattern про процесс, инструкции, выбор tool'а, mechanism». Я расширил в SKILL.md и README до «процесс, инструкции, mechanisms, шероховатости» + broad workflow. Через 2 хода user clarified «только AI работа, жёсткая граница с `1findings`».

## Possible upgrade

Когда user даёт scope-related instruction для нового layer / папки / skill — **до** написания broad framing задать через `AskUserQuestion` уточняющий вопрос про границу. Особенно когда: (a) layer новый и boundary неявная, (b) есть соседний skill с overlapping scope (тут — `1findings`).

Альтернативно: дефолт narrow rather than broad; в первой итерации писать минимальный scope, пусть user расширяет. Narrow → expansion дешевле reversal, чем broad → narrow.

Применимо к любым SKILL.md / AGENTS.md / criteria-file edits, где scope не очевиден из user signal в одну фразу.
