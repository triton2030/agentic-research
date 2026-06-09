# Code-aware tooling — research snapshot Q2 2026

Source-backed снимок индустрии за период **март – май 2026** по теме:
эмбеддинги, графы зависимостей, retrieval и context engineering применительно
к работе агента с кодом. Снимок собран 20 мая 2026.

Слой — research evidence (staging). Принципы и решения отсюда переезжают в
`knowledge/wisdom-*.md`, `_ops/rules/` или owner-инструкции только после
повторного применения в нескольких сессиях; пока — материал для будущего
authoring.

## Период

Март — май 2026. Что вышло до этого окна цитируется только когда без него
не понять контекст находки 2026 года (например, релиз LSP support в Claude
Code 2.0.74 в декабре 2025).

## Topline findings

1. **Индустрия откатилась от embedding-based code RAG к agentic search +
   structural выжимке.** Claude Code, Cursor, Codex CLI, Aider, Continue,
   Windsurf — все используют grep/ripgrep как primary search, embeddings —
   только как опциональный supplementary layer. Источник: Cherny на HN,
   процитировано в Vadim's blog и MindStudio.

2. **Aider's RepoMap стал de facto pattern** для cold-start orientation в
   незнакомой кодовой базе. Tree-sitter извлекает definitions / references,
   NetworkX строит directed reference graph между файлами, PageRank с
   personalization vector ранжирует, token-budget cuts output. **Без
   эмбеддингов**. 130+ языков поддержки, 40+ с полным repo map. Источник:
   DeepWiki Aider repository-mapping.

3. **Cursor пошёл по пути усиления grep, а не замены его эмбеддингами.**
   Они построили sparse n-gram indexing + memory-mapped file access и
   выпустили `SWE-grep-mini` — модель, специально дообученную под grep-based
   retrieval. Архитектурный сигнал: вкладываться в text search, а не
   переключаться на dense retrieval. Источник: yage.ai.

4. **LSP теперь native в Claude Code** (с версии 2.0.74, декабрь 2025), но в
   реальной работе агент редко его триггерит. Один HN-комментатор:
   *"I haven't come across a case where it has used the LSP yet."* LSP
   функционирует как optional precision layer, не как primary backbone.
   Источник: yage.ai, claudecodeai.blog.

5. **Эмбеддинги для кода всё ещё имеют узкие выигрышные сценарии:**
   natural-language queries («где валидируем user input»), renamed-symbol
   resolution, conceptual search в незнакомых больших монорепо. GitHub
   internal benchmarks: semantic search +12.5% accuracy над plain grep на
   больших кодовых базах; ~3× больше relevant context per task. Источник:
   MindStudio, faros.ai.

6. **Hybrid retrieval побеждает на бенчмарках, не чистые подходы.**
   semantic + BM25 + AST parsing + vector indexing вместо replacement
   даёт ~40% context reduction и 10× speed gains. Источник: tastematter,
   supermemory blog.

7. **Появился специализированный benchmark** — **SWE-Context Bench**
   (Zhu et al., 9 Feb 2026): 1,136 real-world issue-resolution tasks из 66
   open-source репозиториев на 8 языках, с human-verified "gold contexts"
   как intermediate signals. Process-oriented evaluation context retrieval,
   не только binary outcome. Источник: emergentmind, arXiv 2602.08316.

## Layered retrieval architecture (consensus pattern)

Конвергенция индустрии на четырёхслойную модель — не "replace", а
"layered funnel". Каждый слой имеет своё место.

| Слой | Инструмент | Зачем | Когда триггерится |
|------|-----------|-------|------------------|
| 1. Text scan | grep / ripgrep | exact match, zero config, all file types | default exploration |
| 2. Structural | tree-sitter / ast-grep | AST-level matching без LSP overhead | precision refinement |
| 3. Symbol nav | LSP | go-to-definition, find-references, rename safety | precision operations phase |
| 4. Semantic | embeddings | fuzzy / conceptual / renamed-symbol fallback | last resort, large unfamiliar repos |

**Failure mode asymmetry** между слоями важен: grep — soft failure (false
positives, recoverable); LSP — hard failure (server crash → execution
derails). Это объясняет почему в high-frequency agent loops grep остаётся
backbone, даже если LSP формально точнее.

Источник: yage.ai layered retrieval section.

## Aider RepoMap — технический разбор

Самый зрелый production-ready pattern для structural code context. Стоит
понимать в деталях, потому что многие другие реализации (hermes-agent,
freebird, NousResearch) копируют именно эту архитектуру.

### Извлечение символов

- Tree-sitter parser per язык с language-specific `tags.scm` query files.
- Captures: `name.definition.*` (функции, классы, переменные) и
  `name.reference.*` (использования).
- Fallback: Pygments lexer tokenization когда reference extraction failed.
- Каждый символ → `Tag` named tuple: `(rel_fname, abs_fname, line, name, kind)`.

### Граф

- **Nodes** = source files (не символы — файлы).
- **Edges** = identifier references caller-file → defining-file.
- **Edge weight** = 1.0 для normal references; 0.1 для self-loops (предотвращает
  изоляцию nodes).

### PageRank с personalization vector

NetworkX `pagerank()` с biasing-вектором (всё значимое получает `100 / len(all_files)`):

- файл в текущем chat context;
- файл упомянут в user text;
- путь содержит user-mentioned identifier.

Это конвертирует абстрактный PageRank в context-aware ranking.

### Token budget

1. Файлы сортируются по PageRank score.
2. Definitions добавляются с накоплением tokens.
3. Cutoff когда budget исчерпан.
4. Truncation с ellipsis если нужно.
5. Token counting optimization: sample every 100th line для больших файлов.

### Cache

- `diskcache.Cache` в `.aider.tags.cache.v{VERSION}/`.
- Key: absolute path. Value: `{"mtime": float, "data": [Tag]}`.
- Invalidation по mtime mismatch.
- Fallback на in-memory dict при SQLite errors.
- `CACHE_VERSION` bump инвалидирует все cache при изменении extraction logic.

### Output

Иерархический tree:

```
aider/
  repomap.py
    class RepoMap
      def __init__(...)
      def get_repo_map(...)
```

Источник: DeepWiki Aider/4.1-repository-mapping.

## Code embedding models 2026 (если понадобится Layer 4)

| Модель | Что | Особенности |
|--------|-----|------------|
| voyage-code-3 | code-specialized | designed for code understanding |
| Jina Code Embeddings V2 | code similarity | 8192 context, late chunking |
| Nomic Embed Code | open-source code | retrieval-optimized |
| Gemini Embedding 2 | code retrieval | MTEB Code: 84.0 (топ) |

MTEB Code benchmark — индустриальный baseline для сравнения. BGE-M3
(который мы используем в md-navigator) — general multilingual, **не**
code-specialized; для кода будет хуже специализированных.

Источник: pecollective, milvus blog, modal blog.

## Where embeddings still win for code (narrow scenarios)

Чтобы не отбросить весь слой целиком — задокументированные сценарии где
embeddings обходят grep:

1. **Natural-language queries**: "найди все места где валидируется ввод
   пользователя" — exact match не работает, semantic similarity работает.
   Источник: MindStudio.
2. **Renamed symbols**: `createD1HttpClient` → `buildGatewayClient`.
   Embeddings preserve semantic relationship, grep — нет. LSP rename solves
   forward, embeddings solve reverse (find old references когда rename не
   зафиксирован). Источник: vadim.blog.
3. **Conceptual search в больших unfamiliar монорепо**: с inconsistent
   naming — embeddings ловят то, что grep пропускает. GitHub internal:
   +12.5% accuracy. Источник: digitalapplied.
4. **Multi-tenant SaaS systems**: vector DB permission scoping через
   metadata filtering. Не наш use case, но в индустрии валидный.
   Источник: MindStudio.

## Numbers / benchmarks (для калибровки)

- **Aider RepoMap context utilization**: 4.3–6.5% (vs 54–70% для iterative
  search agents без RepoMap). Источник: WebSearch results, repomap research.
- **Amazon Science Feb 2026** (arXiv 2602.23368): keyword search via agentic
  tool use achieves **>90%** of RAG-level performance без vector DB.
  Источник: vadim.blog, MindStudio.
- **Hybrid retrieval** (semantic + BM25 + AST + vector): **40%** context
  reduction, **10×** speed gains. Источник: tastematter.
- **GitHub Copilot semantic search**: ~**3×** more relevant context per task
  vs keyword-only; **+12.5%** accuracy over grep на больших кодовых базах.
  Источник: digitalapplied.
- **Cursor SWE-grep-mini**: **4×** latency reduction через parallel tool
  calls (4–12 simultaneously вместо sequential), 20-turn sessions ушли с
  20–40s на 5-turn 4–5s. Источник: vadim.blog.
- **Anthropic prompt caching в Claude Code**: **92%** prefix reuse, **81%**
  cost reduction (от $6.00 до $1.152 per 2M-token session). Источник:
  vadim.blog.

## Claude Code как сейчас работает с кодом (baseline)

Чтобы понимать что строить поверх — текущая baseline:

- **Tool hierarchy в порядке cost**: Glob (≈0 tokens) → Grep (lightweight)
  → Read (500-1,500 tokens per file). Прогрессивный refinement.
- **Explore sub-agent**: Haiku модель в isolated context может grep / glob /
  read / limited bash, возвращает summaries вместо raw content. Это уже
  встроенный pattern для "iterative exploration без burn основного контекста".
- **Five-layer compaction**: Tool Result Budget → Snip → Microcompaction →
  Context Collapse → Autocompact. Threshold = `effectiveWindow - 13000`.
- **Session Memory** background extraction каждые 8K initial / 15K
  incremental tokens, в отдельную persistent summary.
- **Native LSP support** (2.0.74, дек 2025) — есть, но user adoption низкий.
- **Skills + MCP** — primary mechanism для extension.

Источник: zainhas.github.io inside-claude-code-architecture, callsphere.

## Implications для нашего полигона (objective signals)

Без рекомендаций — только сигналы, которые меняют decision-space:

- **Layer 1 (grep) — у Claude Code уже сильный**, оптимизация под параллельность,
  retry на EAGAIN, ignore patterns. Дублировать не имеет смысла.
- **Layer 2 (structural) — gap.** RepoMap-style выжимки на cold-start в Claude
  Code нет встроенно. Это конкретный bypass-able gap.
- **Layer 3 (LSP) — есть, но недоиспользуется агентом.** Skill / instruction
  could увеличить triggering без новой инфраструктуры.
- **Layer 4 (embeddings) — пользуется только в narrow cases.** Строить под
  это с нуля — низкий ROI, особенно учитывая что наша md-embedding инфра не
  переносится напрямую (BGE-M3 general, не code-tuned; chunking heading-based,
  не AST-based).
- **md-navigator архитектура частично переносима** (sqlite per corpus, BM25F +
  dense RRF), но chunking логику нужно переписывать (tree-sitter вместо
  headings) и embedding модель менять (voyage-code-3 / Jina code / Nomic).
- **Aider RepoMap уже open-source**, в Python, MIT-license, изолируется в
  отдельный модуль — потенциально пригодная заготовка вместо построения с нуля.
- **Готовые MCP servers** уже существуют (Code Pathfinder, LSP Bridge,
  Semgrep MCP, ast-grep MCP) — потенциальный shortcut.

## Open questions (для следующего research dive)

1. Воспроизводимы ли Aider's RepoMap numbers (4.3-6.5% context util) вне
   Aider's runtime — в Claude Code agentic loop? Не нашёл независимых replications.
2. Real-world adoption Cursor's SWE-grep-mini — какие numbers вне Cursor's
   blog post? Independent benchmarks отсутствуют в публичном поле.
3. Какой conversion rate "LSP установлен" → "LSP реально триггерится агентом"?
   Anecdotal "haven't seen it used" недостаточно.
4. SWE-Context Bench — какие подходы реально побеждают на нём? Бенчмарк свежий
   (февраль 2026), leaderboard ещё мал.
5. Стоимость code embeddings в production: $voyage-code-3 / 1M tokens vs
   trade-off в качестве. Cost-benefit не разобран.

## Sources

### Industry analysis / opinion
- [Coding Agents Skipped RAG — RAG Still Wins on Large Docs (MindStudio)](https://www.mindstudio.ai/blog/is-rag-dead-what-ai-coding-agents-use-instead)
- [Claude Code Doesn't Index Your Codebase — Vadim's blog](https://vadim.blog/claude-code-no-indexing)
- [Why Coding Agents Still Use grep — yage.ai (March 2026)](https://yage.ai/share/why-coding-agents-still-use-grep-en-20260327.html)
- [Why Claude Code is Special for Not Doing RAG — Aram (Medium)](https://zerofilter.medium.com/why-claude-code-is-special-for-not-doing-rag-vector-search-agent-search-tool-calling-versus-41b9a6c0f4d9)
- [Agentic Search Over Vector Embeddings — agentic-patterns.com](https://www.agentic-patterns.com/patterns/agentic-search-over-vector-embeddings/)

### Aider RepoMap (technical)
- [Aider Repository Mapping System — DeepWiki](https://deepwiki.com/Aider-AI/aider/4.1-repository-mapping)
- [Enrich repo_map with tree-sitter PageRank — JoshCap20/freebird](https://github.com/JoshCap20/freebird/issues/136)
- [PageRank Repo Map feature — NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent/issues/535)

### Tree-sitter chunking
- [Large codebase context with tree-sitter and Cocoindex](https://cocoindexio.substack.com/p/index-codebase-with-tree-sitter-and)
- [Building code-chunk: AST Aware Code Chunking — supermemory](https://supermemory.ai/blog/building-code-chunk-ast-aware-code-chunking/)
- [Real-Time Semantic Code Search With Tree-sitter — Towards AI](https://pub.towardsai.net/building-real-time-semantic-code-search-with-tree-sitter-and-vector-embeddings-b9b1fc0a94f3)
- [How I Built CodeRAG with Dependency Graph Using Tree-Sitter](https://medium.com/@shsax/how-i-built-coderag-with-dependency-graph-using-tree-sitter-0a71867059ae)
- [Building RAG on codebases (Part 1) — LanceDB](https://www.lancedb.com/blog/building-rag-on-codebases-part-1)
- [Semantic Code Indexing with AST and Tree-sitter — Medium](https://medium.com/@email2dineshkuppan/semantic-code-indexing-with-ast-and-tree-sitter-for-ai-agents-part-1-of-3-eb5237ba687a)

### Claude Code architecture
- [Inside Claude Code: An Architecture Deep Dive — Zain Hasan](https://zainhas.github.io/blog/2026/inside-claude-code-architecture/)
- [Claude Code Source Leak: Three-Layer Memory Architecture (MindStudio)](https://www.mindstudio.ai/blog/claude-code-source-leak-three-layer-memory-architecture)
- [Claude Code's Tool System Explained — CallSphere](https://callsphere.ai/blog/claude-code-tool-system-explained)
- [Claude Code LSP Setup Guide](https://claudecodeai.blog/claude-code-lsp-setup-guide-real-time-code-intelligence/)
- [Native AL Language Server Support in Claude Code — SShadowS](https://blog.sshadows.dk/2026/01/09/native-al-language-server-support-in-claude-code/)
- [Claude Code Sees Like A Software Architect — Dave Griffith](https://davegriffith.substack.com/p/claude-code-sees-like-a-software)

### Embedding models comparison
- [10 Best Embedding Models 2026 — Openxcell](https://www.openxcell.com/blog/best-embedding-models/)
- [Best Embedding Models 2026: MTEB + Pricing — pecollective](https://pecollective.com/tools/best-embedding-models/)
- [Best Embedding Models for RAG 2026 — Milvus](https://milvus.io/blog/choose-embedding-model-rag-2026.md)
- [6 Best Code Embedding Models Compared — Modal](https://modal.com/blog/6-best-code-embedding-models-compared)
- [Which Embedding Model Should You Use 2026 (benchmark) — Cheney Zhang](https://zc277584121.github.io/rag/2026/03/20/embedding-models-benchmark-2026.html)

### Dependency graph / AST tools
- [Semgrep Supply Chain Dependency Graph](https://semgrep.dev/products/product-updates/announcing-dependency-graph-on-semgrep-supply-chain/)
- [SCIP — Sourcegraph indexing format](https://sourcegraph.com/blog/announcing-scip)
- [ast-grep tool comparison](https://ast-grep.github.io/advanced/tool-comparison.html)
- [Code Pathfinder MCP — semantic code analysis](https://codepathfinder.dev/mcp)
- [ast-grep with AI Tools — official docs](https://ast-grep.github.io/advanced/prompting.html)

### Benchmarks
- [SWE-Context Bench for Software Agents — emergentmind](https://www.emergentmind.com/topics/swe-context-bench)
- [SWE-Bench Coding Agent Leaderboard 2026 — Awesome Agents](https://awesomeagents.ai/leaderboards/swe-bench-coding-agent-leaderboard/)
- [SWE-Bench original](https://www.swebench.com/original.html)
- [Code Retrieval Techniques in Coding Agents (preprints, 2602.23368)](https://www.preprints.org/manuscript/202510.0924)

### LSP integration
- [LSP Integration for Claude Code Skill — mcpmarket](https://mcpmarket.com/tools/skills/lsp-integration-for-claude-code)
- [LSP Management Claude Code Skill — mcpmarket](https://mcpmarket.com/tools/skills/lsp-management)
- [LSP Bridge MCP — mcpmarket](https://mcpmarket.com/server/lsp-bridge-1)
- [Give Your AI Coding Agent Eyes — Maik Kingma (the/experts)](https://tech-talk.the-experts.nl/give-your-ai-coding-agent-eyes-how-lsp-integration-transform-coding-agents-4ccae8444929)
- [LSP: The Secret Weapon for AI Coding Tools — Amir Teymoori](https://amirteymoori.com/lsp-language-server-protocol-ai-coding-tools/)
- [Anthropic Language Server Integration — DeepWiki](https://deepwiki.com/anthropics/claude-plugins-official/5-language-server-integration)

### Context engineering
- [State of Context Engineering 2026 — Aurimas Griciūnas](https://www.newsletter.swirlai.com/p/state-of-context-engineering-in-2026)
- [Context Engineering Complete Guide April 2026 — supermemory](https://supermemory.ai/blog/what-is-context-engineering-complete-guide/)
- [Effective context engineering for AI agents — Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Codified Context: Infrastructure for AI Agents (arXiv 2602.20478)](https://arxiv.org/html/2602.20478v1)
- [State of AI Coding Agents 2026 — Dave Patten](https://medium.com/@dave-patten/the-state-of-ai-coding-agents-2026-from-pair-programming-to-autonomous-ai-teams-b11f2b39232a)

### Claude Code skills / plugins ecosystem
- [Claude Code Plugin Marketplace Guide 2026 — agensi.io](https://www.agensi.io/learn/claude-code-plugin-marketplace-guide)
- [Top 50 Claude Skills and Github Repos 2026 — blockchain-council](https://www.blockchain-council.org/claude-ai/top-50-claude-skills-and-github-repos/)
- [313+ Claude Code Skills Repository — alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)
- [Claude Code Skills Collection — glebis/claude-skills](https://github.com/glebis/claude-skills)
- [Claude Code Plugins + Skills (jeremylongshore)](https://github.com/jeremylongshore/claude-code-plugins-plus-skills)
- [Hex-graph code knowledge graph MCP — levnikolaevich/claude-code-skills](https://github.com/levnikolaevich/claude-code-skills)
