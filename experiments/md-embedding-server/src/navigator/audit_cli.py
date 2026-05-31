"""Retired legacy audit CLI surface.

The legacy argparse audit dispatchers were removed when the legacy CLI
layer was retired. The `md` CLI now calls `navigator.api.audit`, which
delegates to `navigator.audit.audit_payload`; human rendering lives in
`navigator.audit_render.render_audit`.

This module is intentionally kept (without the CLI functions) so the
architecture-boundary test that pins the render / severity / detection
split keeps a stable target.
"""

from __future__ import annotations
