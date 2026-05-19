# Guardrail Instead Of Removal

## Observation

Когда user говорит убрать нежелательный путь, модель иногда сначала делает
"запрещено по умолчанию, но можно включить флагом". Это сохраняет именно тот
люк, который user хотел удалить.

## Counter

- 2026-05-20 [GPT-5.5]: при переводе Claude/Gemini bridge на аккаунтный CLI я
  сначала оставил explicit API/Vertex/API-key escape hatch. User поправил:
  "надо чтобы они оба ели мой аккаунт а не апи кредиты" и "удалить ... вещи
  которые на всякий случай".

## Possible upgrade

Если user использует формулировки "а не", "удалить", "не надо на всякий
случай", default должен быть deletion of alternate path, not guardrail flag.
