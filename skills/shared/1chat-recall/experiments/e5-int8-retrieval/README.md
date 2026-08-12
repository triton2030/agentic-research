# E5 INT8 retrieval prototype

Archived model-based retrieval route for `1chat-recall`. It is evidence and
reusable code, not part of the live skill runtime.

## Selected model

- model: `intfloat/multilingual-e5-small`
- revision: `614241f622f53c4eeff9890bdc4f31cfecc418b3`
- embedding dimension: `384`
- runtime form: ONNX dynamic `QInt8`
- retrieval: dense top 8 interleaved with lexical top 48, then bounded
  session and identifier relations
- model file is intentionally not committed; the script can quantize a local
  FP32 ONNX model and build a snapshot-bound embedding cache

## Preserved artifact

`int8_dense_probe.py` is an exact copy of the final frozen probe from:

`_workspace/orchestration/2026-08-11-chat-recall-mavo-holdout/int8_dense_probe.py`

Preserved SHA-256:

`c11370d51d0de83b0fddc81d1b1ea374d5631e9df0073c610d474a3723a5cc06`

The script owns quantization, cache construction, hybrid acquisition,
bounded packets, separate-process benchmarking, footprint measurement and
assessment.

## Measured result

The route was rejected only by the experiment's original strict latency gate:
warm separate-process p95 was `1.078124 s` against `<1.0 s`. First-process
wall time was `1.412077 s`. The owner later clarified that this threshold was
too literal; the model route remains a useful preserved candidate.

Frozen model evidence from that run:

- QInt8 ONNX: `118101091 B`
- model SHA-256:
  `8da4c9ba0ad59f58e8566839425d7fd6339d31414d0ce5cba2d7d0afb75dd8b6`
- isolated embedding cache: `998866 B`
- model plus cache stayed below the `150 MB` experiment ceiling

## Status

Do not import or call this prototype from live `SKILL.md`,
`chat_recall.py` or `chat_digest.py` without a new behavioral comparison.
The current product frame permits a local model/cache bootstrap and several
seconds for a consequential query, but this archived experiment does not by
itself prove fresh-agent selection quality.
