from pathlib import Path

import pytest

from clickup_control.safety import ConfirmationRequiredError, PreviewStore, is_read_method


def test_read_method_does_not_need_preview() -> None:
    assert is_read_method("GET") is True
    assert is_read_method("POST") is False


def test_preview_token_is_bound_to_body_and_consumed(tmp_path: Path) -> None:
    store = PreviewStore(tmp_path)
    preview = store.create("POST", "/v2/list/42/task", {}, {"name": "One"})
    assert preview.as_dict()["expires_at_iso"].endswith("+00:00")

    with pytest.raises(ConfirmationRequiredError, match="does not match"):
        store.consume(
            preview.token,
            "POST",
            "/v2/list/42/task",
            {},
            {"name": "Two"},
        )

    store.consume(preview.token, "POST", "/v2/list/42/task", {}, {"name": "One"})
    with pytest.raises(ConfirmationRequiredError, match="already used"):
        store.consume(preview.token, "POST", "/v2/list/42/task", {}, {"name": "One"})
