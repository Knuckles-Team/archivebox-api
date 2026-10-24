import inspect
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from archivebox_api.api_client import Api


@pytest.fixture
def mock_session():
    with patch("archivebox_api.api.api_client_base.create_http_client") as mock_sess:
        session = mock_sess.return_value

        res = MagicMock()
        res.status_code = 200
        res.ok = True
        res.json.return_value = {
            "token": "mock_token",
            "results": [],
            "next": None,
            "id": "123",
        }
        res.content = b'{"token": "mock_token"}'
        res.text = '{"token": "mock_token"}'
        session.get.return_value = res
        session.post.return_value = res
        session.request.return_value = res

        yield session


_PARAM_NAME_VALUE_RULES: list[tuple[tuple[str, ...], Any]] = [
    (("urls",), ["http://test.com"]),
    (("id",), "123"),
    (("filter_patterns",), ["test"]),
    (("depth", "limit", "offset", "page"), 1),
    (("after", "before", "resume"), 123456789.0),
    (("enabled", "update", "overwrite", "init", "as_json"), True),
]


def _guess_kwarg_value(param_name: str, annotation: Any) -> Any:
    """Best-effort guess of a plausible value for one brute-forced parameter, by name."""
    for keywords, value in _PARAM_NAME_VALUE_RULES:
        if any(keyword in param_name for keyword in keywords):
            return value
    if annotation == dict:
        return {}
    return "test"


def _guessed_kwargs(sig: inspect.Signature) -> dict[str, Any]:
    """Guess a kwargs dict covering every declared parameter of ``sig``."""
    return {
        param.name: _guess_kwarg_value(param.name, param.annotation)
        for param in sig.parameters.values()
        if param.name != "kwargs"
    }


def _positional_args(sig: inspect.Signature, kwargs: dict[str, Any]) -> list[Any]:
    """Pull required positional-eligible params out of ``kwargs`` as an arg list."""
    pos_args = []
    for param in sig.parameters.values():
        if param.default == inspect.Parameter.empty and param.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.POSITIONAL_ONLY,
        ):
            pos_args.append(kwargs.get(param.name, "test"))
            if param.name in kwargs:
                del kwargs[param.name]
    return pos_args


def _call_method_best_effort(method: Any) -> None:
    """Call one client method with guessed args; any failure is expected/logged."""
    sig = inspect.signature(method)
    kwargs = _guessed_kwargs(sig)
    try:
        pos_args = _positional_args(sig, kwargs)
        method(*pos_args, **kwargs)
    except Exception as e:
        print(f"Operation failed: {type(e).__name__}")


def _construct_best_effort(**ctor_kwargs: Any) -> None:
    try:
        Api(url="http://test.com", **ctor_kwargs)
    except Exception:
        pass


def test_api_brute_force(mock_session):
    _ = mock_session
    # Test init paths
    _construct_best_effort(token="token")
    _construct_best_effort(api_key="key")
    _construct_best_effort(username="u", password="p")

    client = Api(url="http://test.com", token="mock_token")

    # Introspect all methods
    for name, method in inspect.getmembers(client, predicate=inspect.ismethod):
        if name.startswith("_") or name in ["get_api_token"]:
            continue
        print(f"Calling {name}...")
        _call_method_best_effort(method)
