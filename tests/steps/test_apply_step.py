"""Behavior tests for ApplyStep."""

import logging

import pytest

from flowstep.core import FlowContext
from flowstep.steps import ApplyStep


def test_execute_applies_single_transform_and_writes_output_key() -> None:
    step = ApplyStep(
        "double", lambda values: [v * 2 for v in values], input_key="in", output_key="out"
    )
    context = FlowContext({"in": [1, 2, 3]})

    step.execute(context)

    assert context.get("out") == [2, 4, 6]


def test_execute_applies_transforms_left_to_right() -> None:
    step = ApplyStep(
        "chain",
        lambda values: [v + 1 for v in values],
        lambda values: [v * 2 for v in values],
        input_key="in",
        output_key="out",
    )
    context = FlowContext({"in": [1, 2]})

    step.execute(context)

    # (v + 1) * 2, transforms applied in declaration order: add-one then double
    assert context.get("out") == [4, 6]


def test_execute_with_zero_transforms_passes_value_through_unchanged() -> None:
    step = ApplyStep("noop", input_key="in", output_key="out")
    context = FlowContext({"in": [1, 2, 3]})

    step.execute(context)

    assert context.get("out") == [1, 2, 3]


def test_get_required_keys_returns_input_key() -> None:
    step = ApplyStep("step", input_key="in", output_key="out")

    assert step.get_required_keys() == {"in"}


def test_get_produced_keys_returns_output_key() -> None:
    step = ApplyStep("step", input_key="in", output_key="out")

    assert step.get_produced_keys() == {"out"}


def test_execute_does_not_emit_any_log_records(caplog: pytest.LogCaptureFixture) -> None:
    step = ApplyStep("silent", input_key="in", output_key="out")
    context = FlowContext({"in": [1, 2, 3]})

    with caplog.at_level(logging.DEBUG):
        step.execute(context)

    assert caplog.records == []
