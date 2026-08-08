## Candidate Canvas and Invocation

The complete installed set of model-invoked descriptions is the authoring-time
candidate canvas. Runtime co-presence is not guaranteed, so a broad or adjacent
trigger also needs checking against the prompt surface actually visible to the
model.

- A shared trigger phrase is a collision/ownership question, not literal
  deduplication.
- Resolve collisions by narrowing the positive triggers of the owners. Keep
  near-miss cases in evaluation, not as neighbor pointers in runtime text.
- `disable-model-invocation: true` suits a deliberate/manual skill that should
  not compete in model discovery.
- Verify the live Claude skill root and resolved model rather than inferring
  them from an alias, old path, or another platform.
