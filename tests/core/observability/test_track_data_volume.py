"""Behavior tests for the track_data_volume context manager."""

import pytest
from conftest import MakeStep, RecordingDataVolumeObserver

from flowstep.core import FlowContext
from flowstep.core.observability import track_data_volume


def test_reports_input_and_output_sizes_on_success(make_step: MakeStep) -> None:
    observer = RecordingDataVolumeObserver()
    step = make_step(name="step")
    context = FlowContext({"in": [1, 2, 3]})

    with track_data_volume(observer, step, context, "in", "out"):
        context.put("out", [1, 2])

    assert observer.calls == [("step", 3, 2)]


def test_reports_none_when_input_is_not_sized(make_step: MakeStep) -> None:
    observer = RecordingDataVolumeObserver()
    step = make_step(name="step")
    context = FlowContext({"in": (v for v in [1, 2, 3])})

    with track_data_volume(observer, step, context, "in", "out"):
        context.put("out", [1, 2, 3])

    assert observer.calls == [("step", None, 3)]


def test_uses_pre_block_input_value_even_when_input_and_output_keys_match(
    make_step: MakeStep,
) -> None:
    observer = RecordingDataVolumeObserver()
    step = make_step(name="step")
    context = FlowContext({"data": [1, 2, 3]})

    with track_data_volume(observer, step, context, "data", "data"):
        context.put("data", [1, 2])

    assert observer.calls == [("step", 3, 2)]


def test_does_not_notify_observer_when_block_raises(make_step: MakeStep) -> None:
    observer = RecordingDataVolumeObserver()
    step = make_step(name="step")
    context = FlowContext({"in": [1, 2, 3]})

    with (
        pytest.raises(ValueError, match="boom"),
        track_data_volume(observer, step, context, "in", "out"),
    ):
        raise ValueError("boom")

    assert observer.calls == []
