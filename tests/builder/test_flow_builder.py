"""Behavior tests for FlowBuilder."""

import logging

import pytest
from conftest import MakeStep, RecordingFlowObserver

from flowstep.builder import FlowBuilder
from flowstep.core import Flow, LoggingFlowObserver, Step, StepProgress
from flowstep.validation.exceptions import FlowValidationError

_LOGGER_NAME = "flowstep.core.observability.logging_flow_observer"


def test_build_returns_flow_with_added_steps(make_step: MakeStep) -> None:
    step_a = make_step(name="a")
    step_b = make_step(name="b")

    flow = FlowBuilder("pipeline").add_step(step_a).add_step(step_b).build()

    assert isinstance(flow, Flow)
    assert flow.get_steps() == [step_a, step_b]


def test_build_without_validate_skips_validation(make_step: MakeStep) -> None:
    duplicate_a = make_step(name="dup")
    duplicate_b = make_step(name="dup")

    flow = FlowBuilder("pipeline").add_step(duplicate_a).add_step(duplicate_b).build()

    assert flow.get_steps() == [duplicate_a, duplicate_b]


def test_build_with_validate_raises_on_error(make_step: MakeStep) -> None:
    duplicate_a = make_step(name="dup")
    duplicate_b = make_step(name="dup")

    builder = FlowBuilder("pipeline").add_step(duplicate_a).add_step(duplicate_b)

    with pytest.raises(FlowValidationError):
        builder.build(validate=True)


def test_build_with_validate_passes_when_contract_is_satisfied(make_step: MakeStep) -> None:
    step = make_step(name="step", required_keys=set(), produced_keys={"output"})

    flow = FlowBuilder("pipeline").add_step(step).build(validate=True)

    assert isinstance(flow, Flow)


def test_build_with_validate_uses_initial_context_keys(make_step: MakeStep) -> None:
    step = make_step(name="step", required_keys={"input"})

    flow = (
        FlowBuilder("pipeline")
        .add_step(step)
        .build(validate=True, initial_context={"input": "value"})
    )

    assert isinstance(flow, Flow)


def test_add_observer_returns_self_for_chaining() -> None:
    builder = FlowBuilder("pipeline")

    result = builder.add_observer(RecordingFlowObserver())

    assert result is builder


def test_build_flow_notifies_registered_observer_on_run(make_step: MakeStep) -> None:
    observer = RecordingFlowObserver()
    step = make_step(name="step")

    flow = FlowBuilder("pipeline").add_step(step).add_observer(observer).build()
    flow.run()

    assert [call[0] for call in observer.calls] == ["on_start", "on_end"]
    assert observer.calls[0][1] == "step"


def test_build_flow_uses_default_logging_observer_without_add_observer(
    make_step: MakeStep, caplog: pytest.LogCaptureFixture
) -> None:
    step = make_step(name="step")
    flow = FlowBuilder("pipeline").add_step(step).build()

    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        flow.run()

    assert any("step" in record.getMessage() for record in caplog.records)


def test_build_flow_notifies_both_default_logging_and_custom_observer(
    make_step: MakeStep, caplog: pytest.LogCaptureFixture
) -> None:
    observer = RecordingFlowObserver()
    step = make_step(name="step")

    flow = FlowBuilder("pipeline").add_step(step).add_observer(observer).build()

    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        flow.run()

    assert any("step" in record.getMessage() for record in caplog.records)
    assert [call[0] for call in observer.calls] == ["on_start", "on_end"]


def test_build_flow_calls_default_logging_observer_before_custom_observer_on_start(
    make_step: MakeStep, monkeypatch: pytest.MonkeyPatch
) -> None:
    call_order: list[str] = []
    original_on_start = LoggingFlowObserver.on_start

    def recording_on_start(self: LoggingFlowObserver, step: Step, progress: StepProgress) -> None:
        call_order.append("logging")
        original_on_start(self, step, progress)

    monkeypatch.setattr(LoggingFlowObserver, "on_start", recording_on_start)

    class OrderTrackingObserver:
        def on_start(self, step: object, progress: StepProgress) -> None:
            call_order.append("custom")

        def on_end(self, step: object, duration_ms: float, progress: StepProgress) -> None:
            pass

        def on_error(self, step: object, error: Exception, progress: StepProgress) -> None:
            pass

    step = make_step(name="step")
    flow = FlowBuilder("pipeline").add_step(step).add_observer(OrderTrackingObserver()).build()
    flow.run()

    assert call_order == ["logging", "custom"]
