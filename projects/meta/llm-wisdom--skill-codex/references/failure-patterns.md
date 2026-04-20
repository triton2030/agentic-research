# Failure Patterns

These are recurring ways model quality degrades even when the answer sounds polished.

## Hallucination

- The model invents facts, files, behavior, or sources that fit the pattern of the task.
- Often worsens when stale memory or generic pattern completion replaces a read of the current artifact.
- Better lever: require direct reads, fresh evidence, or current-state verification.

## Scope drift

- The model quietly redefines the task into something easier or cleaner.
- Common sign: the output is strong, but it solves an adjacent problem.
- Better lever: restate the exact target and forbid paraphrase-as-spec.

## Confidence theatre

- The answer uses "clearly", "obviously", or smooth language to hide uncertainty.
- Better lever: replace self-report with observable artifacts or mark uncertainty explicitly.

## Summary instead of contact

- The model produces a plausible summary without engaging deeply with the source artifact.
- Better lever: require a concrete cite-back to a function, key, section, or line.

## Local optimization

- The model chooses the easiest formal pass instead of the truest fix.
- Better lever: define what would count as fake success and block it upfront.
