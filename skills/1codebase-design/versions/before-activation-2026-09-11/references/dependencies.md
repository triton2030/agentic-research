# Dependency and Seam Decisions

Use this reference when dependency behavior materially affects seam placement
or verification.

## Dependency Pressure

Classify only far enough to expose the real design constraint:

- **In-process computation:** usually needs no adapter. Keep the seam only when
  it owns meaningful policy or variation.
- **Local substitute available:** a realistic local implementation can support
  behavior-level tests without exposing the dependency through the module's
  public interface.
- **Remote and owned:** transport is a real operational seam. Keep domain policy
  on one side and isolate transport, retries, serialization, and availability
  assumptions in an adapter or port when that reduces caller knowledge.
- **External and unowned:** keep vendor latency, rate limits, and failure detail
  inside the adapter unless they change caller-visible outcomes or correct
  recovery. Translate material obligations at the owning boundary.

These categories inform a decision; none automatically requires merging,
ports, mocks, or a particular architecture.

## A Justified Seam

A dependency seam should describe the capability the owning module needs, not
mirror the dependency's SDK.

One production adapter plus a purpose-built test double may justify a seam when
the external effect is real and the double preserves behavior relevant to the
contract. A convenient fake that erases concurrency, persistence, or failure
semantics can make the design less testable, not more.

## Test Consequences

In-process and realistic local substitutes can often be proved through the
module contract. Remote or unowned adapters need the smallest integration or
contract check that can falsify their transport and translation obligations.

An old test may go when its obligation is obsolete or intentionally removed,
or its distinct risk is proved elsewhere. Survival across refactors is useful
evidence of a good boundary, not an absolute requirement for every test.
