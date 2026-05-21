# Threshold From Single Corpus

## Observation

Модель калибрует diagnostic threshold (audit / lint / metric)
**против одного знакомого корпуса** и принимает его как universal
default. На внешнем корпусе с другим стилем порог даёт радикально
другую false-positive rate.

Pattern: **calibration-on-known**. Default выглядит правильным потому
что я его проверил на корпусе, который сам ежедневно вижу. Кажется
«работает» — но это значит лишь «работает на моём дизайне», не «на
markdown corpora вообще».

## Counter

- 2026-05-20 [Claude Opus 4.7]: heading-lex drift threshold для
  `1md-navigator audit`. Откалибровал на agentic-research/knowledge
  (32 файла, wisdom-стиль с короткими H2 «Опоры / Проверено / Где
  Использовать» — 25 false positives при threshold 0.85). На
  MAVO/Анализ (219 файлов outline-стиля «какую проблему режем / из
  чего состоит модель / главный тест / что читать дальше») тот же
  threshold дал 130 false positives (60% корпуса). Stylistic difference
  (выводы-как-headings vs outline-questions) полностью меняет
  distribution. User поймал бы 130 файлов в info-flood; default не
  выдерживает на другом стиле документации.
- 2026-05-20 [Claude Opus 4.7]: feature decision для `1md-graph`
  anchor pass-through. Измерил `[[file#anchor]]` frequency в
  agentic-research (2 anchor links на 44 wikilinks ≈ 4.5%) → выдал
  рекомендацию «не делать, премия маргинальная». User поправил «скил
  будет работать в MAVO/Анализ». Там 34 anchor links на 1029 (≈3.3%
  но другой масштаб + operational character — принципы, психология,
  путь заказа). Frequency как метрика не переносится через корпуса
  даже когда % похож; характер использования сильнее распределения.
  Decision на одном знакомом корпусе сначала дал false negative.

## Possible upgrade

Перед finalize threshold для diagnostic tool:
- Запустить на ≥2 stylistically different корпусах. Compare false-
  positive rate. Variance > 2× = single-corpus calibration, threshold
  нельзя ship'ить как default.
- Если variance высокая — либо expose threshold prominently в SKILL.md
  (per-corpus tuning expected), либо добавить style-detector (e.g.
  «короткие H2 в последовательности = outline»), либо понизить
  severity для рискованного class.

Применимо: любой metric/heuristic с tunable threshold (search rerank
threshold, similarity cutoffs, diversity cutoffs, lint rules,
embedding-distance gates).

Стилистическая diversity корпусов > diversity моих собственных
интуиций о «нормальной» структуре документации.
