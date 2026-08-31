# API — API Specification

**Purpose:** own the consumer-visible, testable interface contract across
implementations. **Default authority:** `canon`. Near-miss: domain meaning →
DOM; internal change → EDD; lifecycle/rules → SEM/BRC; tutorial → projection.

**Ban:** API owns the wire contract, not domain meaning, business rules or
implementation. A machine spec proves only what it states: never infer purpose,
effects, retry/idempotency or compatibility from HTTP method, status codes or
schemas — without owner evidence the section gets `SECTION-STATUS`.

**Non-obvious contracts:** Representation Authority — one normative home per
interface/version and logical unit (Markdown section or exact machine-spec
component), with stable IDs, direction, drift gate; schemas hold full wire shape
only when Markdown is normative, else REFERENCE + component links. Error
Contract owns semantic codes and retryability, wire status follows the chosen
representation. Auth and Security/Privacy Impact = LOCAL; Companion Spec =
REFERENCE, no duplicated schema; examples nonnormative.

**Conditional modules:** webhooks/events; streaming; batch/file transfer;
callbacks/signing; SDK; multi-tenancy.

**Completion check:** one normative representation per wire contract, with
explicit generation/validation direction.
