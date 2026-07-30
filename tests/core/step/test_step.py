"""Behavior tests for the Step contract."""

import pytest
from conftest import MakeStep, RecordingStepObserver

from flowstep.core import FlowContext


def test_step_name_is_exposed_via_property(make_step: MakeStep) -> None:
    step = make_step(name="load")

    assert step.name == "load"


def test_step_repr_includes_class_and_name(make_step: MakeStep) -> None:
    step = make_step(name="load")

    assert repr(step) == "RecordingStep(name='load')"


def test_execute_runs_custom_behavior(make_step: MakeStep) -> None:
    received: dict[str, FlowContext] = {}

    def on_execute(context: FlowContext) -> None:
        received["context"] = context
        context.put("output", "done")

    step = make_step(name="step", on_execute=on_execute)
    context = FlowContext()

    step.execute(context)

    assert step.executed is True
    assert received["context"] is context
    assert context.get("output") == "done"


def test_get_required_and_produced_keys(make_step: MakeStep) -> None:
    step = make_step(
        name="step",
        required_keys={"input"},
        produced_keys={"output"},
    )

    assert step.get_required_keys() == {"input"}
    assert step.get_produced_keys() == {"output"}


def test_add_observer_returns_self_for_chaining(make_step: MakeStep) -> None:
    step = make_step(name="step")

    result = step.add_observer(RecordingStepObserver())

    assert result is step


def test_call_notifies_observer_on_start_then_on_end_on_success(make_step: MakeStep) -> None:
    observer = RecordingStepObserver()
    step = make_step(name="step").add_observer(observer)

    step(FlowContext())

    assert [call[0] for call in observer.calls] == ["on_start", "on_end"]
    assert observer.calls[0][1] == "step"
    duration_ms = observer.calls[1][2]
    assert duration_ms >= 0


def test_call_notifies_observer_on_start_then_on_error_on_failure(make_step: MakeStep) -> None:
    def failing_execute(_: FlowContext) -> None:
        raise ValueError("boom")

    observer = RecordingStepObserver()
    step = make_step(name="risky", on_execute=failing_execute).add_observer(observer)

    with pytest.raises(ValueError):
        step(FlowContext())

    assert [call[0] for call in observer.calls] == ["on_start", "on_error"]


def test_call_notifies_multiple_observers_in_registration_order(make_step: MakeStep) -> None:
    call_order: list[str] = []

    class OrderTrackingObserver:
        def __init__(self, label: str) -> None:
            self._label = label

        def on_start(self, step: object) -> None:
            call_order.append(self._label)

        def on_end(self, step: object, duration_ms: float) -> None:
            pass

        def on_error(self, step: object, error: Exception) -> None:
            pass

    step = (
        make_step(name="step")
        .add_observer(OrderTrackingObserver("first"))
        .add_observer(OrderTrackingObserver("second"))
    )

    step(FlowContext())

    assert call_order == ["first", "second"]


def test_call_without_observers_still_executes(make_step: MakeStep) -> None:
    step = make_step(name="step")

    step(FlowContext())

    assert step.executed is True
