"""Behavior tests for AsyncApplyStep."""

import asyncio
import logging
from collections.abc import Iterable
from typing import Any

import pytest
from conftest import RecordingDataVolumeObserver

from flowstep.core import FlowContext
from flowstep.steps import AsyncApplyStep

_DATA_VOLUME_LOGGER_NAME = (
    "flowstep.core.observability.data_volume_observers.logging_data_volume_observer"
)


async def _double(values: Iterable[Any]) -> list[Any]:
    return [v * 2 for v in values]


async def _increment(values: Iterable[Any]) -> list[Any]:
    return [v + 1 for v in values]


def test_execute_applies_single_async_transform_and_writes_output_key() -> None:
    step = AsyncApplyStep("double", _double, input_key="in", output_key="out")
    context = FlowContext({"in": [1, 2, 3]})

    step.execute(context)

    assert context.get("out") == [2, 4, 6]


def test_execute_applies_transforms_left_to_right() -> None:
    step = AsyncApplyStep("chain", _increment, _double, input_key="in", output_key="out")
    context = FlowContext({"in": [1, 2]})

    step.execute(context)

    # (v + 1) * 2, transforms applied in declaration order: add-one then double
    assert context.get("out") == [4, 6]


def test_execute_with_zero_transforms_passes_value_through_unchanged() -> None:
    step = AsyncApplyStep("noop", input_key="in", output_key="out")
    context = FlowContext({"in": [1, 2, 3]})

    step.execute(context)

    assert context.get("out") == [1, 2, 3]


def test_get_required_keys_returns_input_key() -> None:
    step = AsyncApplyStep("step", input_key="in", output_key="out")

    assert step.get_required_keys() == {"in"}


def test_get_produced_keys_returns_output_key() -> None:
    step = AsyncApplyStep("step", input_key="in", output_key="out")

    assert step.get_produced_keys() == {"out"}


def test_execute_notifies_data_volume_observer_with_input_and_output_sizes() -> None:
    observer = RecordingDataVolumeObserver()
    step = AsyncApplyStep(
        "double", _double, input_key="in", output_key="out", data_volume_observer=observer
    )
    context = FlowContext({"in": [1, 2, 3]})

    step.execute(context)

    assert observer.calls == [("double", 3, 3)]


def test_execute_uses_default_logging_data_volume_observer_when_none_provided(
    caplog: pytest.LogCaptureFixture,
) -> None:
    step = AsyncApplyStep("double", _double, input_key="in", output_key="out")
    context = FlowContext({"in": [1, 2, 3]})

    with caplog.at_level(logging.INFO, logger=_DATA_VOLUME_LOGGER_NAME):
        step.execute(context)

    assert any("double" in record.getMessage() for record in caplog.records)


def test_transforms_share_a_single_event_loop() -> None:
    loop_ids: list[int] = []

    async def record_loop(values: Iterable[Any]) -> Iterable[Any]:
        loop_ids.append(id(asyncio.get_running_loop()))
        return values

    step = AsyncApplyStep("record", record_loop, record_loop, input_key="in", output_key="out")
    context = FlowContext({"in": [1, 2, 3]})

    step.execute(context)

    assert len(loop_ids) == 2
    assert loop_ids[0] == loop_ids[1]


def test_transforms_run_sequentially_not_concurrently() -> None:
    events: list[str] = []

    async def slow_transform(values: Iterable[Any]) -> Iterable[Any]:
        events.append("slow:start")
        await asyncio.sleep(0.01)
        events.append("slow:end")
        return values

    async def fast_transform(values: Iterable[Any]) -> Iterable[Any]:
        events.append("fast:start")
        events.append("fast:end")
        return values

    step = AsyncApplyStep(
        "sequence", slow_transform, fast_transform, input_key="in", output_key="out"
    )
    context = FlowContext({"in": [1, 2, 3]})

    step.execute(context)

    assert events == ["slow:start", "slow:end", "fast:start", "fast:end"]
