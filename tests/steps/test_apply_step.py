"""Behavior tests for ApplyStep."""

import logging
from collections.abc import Iterable
from typing import Any

import pytest
from conftest import RecordingDataVolumeObserver

from flowstep.core import FlowContext, Step
from flowstep.steps import ApplyStep

_DATA_VOLUME_LOGGER_NAME = (
    "flowstep.core.observability.data_volume_observers.logging_data_volume_observer"
)


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


def test_execute_emits_no_log_records_when_observer_is_a_no_op(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class NoOpDataVolumeObserver:
        def on_processed(self, step: Step, input_size: int | None, output_size: int | None) -> None:
            pass

    step = ApplyStep(
        "silent", input_key="in", output_key="out", data_volume_observer=NoOpDataVolumeObserver()
    )
    context = FlowContext({"in": [1, 2, 3]})

    with caplog.at_level(logging.DEBUG):
        step.execute(context)

    assert caplog.records == []


def test_execute_notifies_data_volume_observer_with_input_and_output_sizes() -> None:
    observer = RecordingDataVolumeObserver()
    step = ApplyStep(
        "double",
        lambda values: [v * 2 for v in values],
        input_key="in",
        output_key="out",
        data_volume_observer=observer,
    )
    context = FlowContext({"in": [1, 2, 3]})

    step.execute(context)

    assert observer.calls == [("double", 3, 3)]


def test_execute_reports_none_size_for_non_sized_input() -> None:
    observer = RecordingDataVolumeObserver()

    def to_list(values: Iterable[Any]) -> list[Any]:
        return list(values)

    step = ApplyStep(
        "materialize", to_list, input_key="in", output_key="out", data_volume_observer=observer
    )
    context = FlowContext({"in": (v for v in [1, 2, 3])})

    step.execute(context)

    assert observer.calls == [("materialize", None, 3)]


def test_execute_uses_default_logging_data_volume_observer_when_none_provided(
    caplog: pytest.LogCaptureFixture,
) -> None:
    step = ApplyStep(
        "double", lambda values: [v * 2 for v in values], input_key="in", output_key="out"
    )
    context = FlowContext({"in": [1, 2, 3]})

    with caplog.at_level(logging.INFO, logger=_DATA_VOLUME_LOGGER_NAME):
        step.execute(context)

    assert any("double" in record.getMessage() for record in caplog.records)
