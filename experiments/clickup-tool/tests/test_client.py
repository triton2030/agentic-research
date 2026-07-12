import pytest

from clickup_control.client import InvalidApiPathError, normalize_api_path


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("v2/user", "/v2/user"),
        ("/v2/team/123/task", "/v2/team/123/task"),
        ("/api/v3/workspaces/123/chat/channels", "/v3/workspaces/123/chat/channels"),
    ],
)
def test_normalize_api_path(value: str, expected: str) -> None:
    assert normalize_api_path(value) == expected


@pytest.mark.parametrize("value", ["https://example.com/v2/user", "/v1/user", "/v2/../admin"])
def test_normalize_api_path_rejects_unsafe_values(value: str) -> None:
    with pytest.raises(InvalidApiPathError):
        normalize_api_path(value)
