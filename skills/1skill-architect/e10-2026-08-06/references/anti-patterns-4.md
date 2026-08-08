# Anti-patterns 4/4 (продолжение, дословно)

- **Matcher-only proof**: showing that a skill can be found, but not that it
  improves the output.
- **Compliance-only proof**: showing that required sections appear, but not that
  an unshown decision, probe, or later trajectory changed.
- **Leaked demonstration**: an eval succeeds only because the expected answer
  or diagnosis was embedded in the thought example.
- **No mechanism ablation**: a central explanation or example is assumed to
  cause the effect without testing whether behavior survives its removal or
  replacement when the claim is material.
- **No near-miss negatives**: testing obvious should-not prompts but not the
  adjacent tasks that actually cause collision.
- **Elastic defense**: a failed run is rescued by a post-hoc explanation when
  no bypass prediction and revision criterion were recorded before it.
- **No sunset signal**: a rule has no observable condition under which it should
  be revisited or removed.
- **Undated model deficit**: a model-dependent limitation has no resolved model,
  observation date, or target-model change trigger for revalidation.

## Language And Priority

- **English voice in Russian truth layer**: mixing language without a reason can
  blur priority and weaken the mental model.
- **Abstract category trigger**: relying on the model to notice "this is design"
  instead of anchoring on visible action, path, artifact, or user phrase.
