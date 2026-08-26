# Topology Contract

Place documents by their role relative to truth, not by the current author's
convenience. A local live convention wins — map it onto these roles first;
never create a parallel tree.

```text
canon/       = what is true or known now
_ops/        = how truth is built, changed, verified and deferred
projections/ = how truth is shown to a specific reader
```

| Zone | Owns | Does not own | Default retrieval |
| --- | --- | --- | --- |
| `canon/` | Current requirements, rules, models, contracts, durable evidence | Plans, rationale history, reader narrative | Yes |
| `_ops/` | Goal, plans, backlog, findings, decisions, change designs, running research, risks, documentation control | Current product/system truth | Only for questions about work, change or rationale |
| `projections/` | Audience-specific composition and visual views | Independent factual truth | No |

`DEC` keeps why a choice was made; an accepted outcome updates the canon
owner. `EDD` describes a planned change; after implementation the current
owners (`ARCH`, `API`, `DOM`, `SEM`…) are updated. Never leave acting truth
only in `_ops/`. Durable `RPT` and concluded `EXP` evidence may live in
`canon/evidence/`.

## Default homes

From [catalog](catalog.md) unless a local registry is stronger. Service homes:
`DOCS`, `MIG` → `_ops/documentation/`; goal → `_ops/GOAL.md` (`1goal`); work →
`_ops/plans/`, `_ops/backlog/` (`1planning`); defects → `_ops/findings/`
(`1findings`); risks → `_ops/risks/`; instruction rules → the live instruction
hierarchy (`1instruction-placement`). Materialize a home together with its first
artifact, never in advance.

## Canon folder algorithm

The filename already encodes genre; a folder encodes a stable domain owner.

1. One current owner per `artifact-type + artifact-scope-key`.
2. Flat root while the whole canon is one coherent owner zone; `canon/<domain>/`
   when artifacts belong to different domain owners or reading flows.
3. One axis per level — never mix type, audience, status and domain folders.
4. No type-folders just because a template exists: the code is visible in the
   name. A second regular reading axis becomes a projection/MOC, not a
   duplicate home.
5. A folder may start with one artifact only when its domain boundary is
   already current and independently routed.

## Router

The Documentation System Map stays a compact link-first router: question →
owner path, admitted type, lifecycle. Current-truth question → `canon/`;
why/when chosen → `_ops/decisions/`; planned/blocked/being-checked → the
relevant `_ops/` owner; audience reading → `projections/` and its lineage.

Before closeout: no empty or future folders · no mixed axes · ops did not
become the only current owner · the map did not become a second canon ·
projections have traceable lineage.
