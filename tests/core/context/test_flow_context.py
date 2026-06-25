"""Behavior tests for FlowContext."""

import pytest

from flowstep.core import FlowContext


def test_put_then_get_returns_stored_value() -> None:
    context = FlowContext()
    context.put("key", "value")

    assert context.get("key") == "value"


def test_get_missing_key_raises_key_error() -> None:
    context = FlowContext()

    with pytest.raises(KeyError):
        context.get("missing")


def test_has_reflects_key_presence() -> None:
    context = FlowContext()

    assert context.has("key") is False

    context.put("key", "value")

    assert context.has("key") is True


def test_initial_data_is_copied_not_aliased() -> None:
    initial_data = {"key": "value"}
    context = FlowContext(initial_data)

    context.put("key", "changed")

    assert initial_data["key"] == "value"


def test_keys_returns_all_stored_keys() -> None:
    context = FlowContext({"a": 1, "b": 2})

    assert context.keys() == {"a", "b"}


def test_to_dict_returns_copy_of_internal_data() -> None:
    context = FlowContext({"a": 1})
    snapshot = context.to_dict()
    snapshot["a"] = 2

    assert context.get("a") == 1
