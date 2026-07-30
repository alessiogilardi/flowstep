"""Behavior tests for Flow execution."""

import logging

import pytest
from conftest import MakeStep, RecordingFlowObserver

from flowstep.core import Flow, FlowContext, FlowProgress
from flowstep.core.exceptions import FlowExecutionError


def test_run_passes_index_and_total_to_observer_for_single_step(make_step: MakeStep) -> None:
    observer = RecordingFlowObserver()
    step = make_step(name="step")

    flow = Flow("pipeline", [step], observer=observer)
    flow.run()

    expected_progress = FlowProgress(index=1, total=1)
    assert observer.calls[0][3] == expected_progress
    assert observer.calls[1][3] == expected_progress


def test_run_passes_increasing_index_across_multiple_steps(make_step: MakeStep) -> None:
    observer = RecordingFlowObserver()
    step_a = make_step(name="a")
    step_b = make_step(name="b")

    flow = Flow("pipeline", [step_a, step_b], observer=observer)
    flow.run()

    progress_by_call = [call[3] for call in observer.calls]
    assert progress_by_call == [
        FlowProgress(index=1, total=2),
        FlowProgress(index=1, total=2),
        FlowProgress(index=2, total=2),
        FlowProgress(index=2, total=2),
    ]


def test_run_executes_steps_in_order(make_step: MakeStep) -> None:
    execution_order: list[str] = []

    step_a = make_step(name="a", on_execute=lambda ctx: execution_order.append("a"))
    step_b = make_step(name="b", on_execute=lambda ctx: execution_order.append("b"))

    flow = Flow("pipeline", [step_a, step_b])
    flow.run()

    assert execution_order == ["a", "b"]


def test_run_seeds_context_from_initial_dict(make_step: MakeStep) -> None:
    observed: dict[str, object] = {}
    step = make_step(name="step", on_execute=lambda ctx: observed.update(value=ctx.get("input")))

    flow = Flow("pipeline", [step])
    flow.run({"input": "seed"})

    assert observed["value"] == "seed"


def test_run_returns_final_context_with_produced_data(make_step: MakeStep) -> None:
    step = make_step(
        name="step",
        produced_keys={"output"},
        on_execute=lambda ctx: ctx.put("output", "result"),
    )

    flow = Flow("pipeline", [step])
    result = flow.run()

    assert isinstance(result, FlowContext)
    assert result.get("output") == "result"


def test_run_wraps_step_exception_in_flow_execution_error(make_step: MakeStep) -> None:
    def failing_execute(_: FlowContext) -> None:
        raise ValueError("boom")

    step = make_step(name="risky", on_execute=failing_execute)
    flow = Flow("pipeline", [step])

    with pytest.raises(FlowExecutionError) as exc_info:
        flow.run()

    assert exc_info.value.step_name == "risky"
    assert isinstance(exc_info.value.original_error, ValueError)


def test_get_steps_returns_copy_not_internal_list(make_step: MakeStep) -> None:
    step = make_step(name="step")
    flow = Flow("pipeline", [step])

    steps = flow.get_steps()
    steps.append(make_step(name="extra"))

    assert flow.get_steps() == [step]


def test_run_calls_observer_on_start_then_on_end_on_success(make_step: MakeStep) -> None:
    observer = RecordingFlowObserver()
    step = make_step(name="step")

    flow = Flow("pipeline", [step], observer=observer)
    flow.run()

    assert [call[0] for call in observer.calls] == ["on_start", "on_end"]
    assert observer.calls[0][1] == "step"
    duration_ms = observer.calls[1][2]
    assert duration_ms >= 0


def test_run_calls_observer_on_start_then_on_error_on_failure(make_step: MakeStep) -> None:
    def failing_execute(_: FlowContext) -> None:
        raise ValueError("boom")

    observer = RecordingFlowObserver()
    step = make_step(name="risky", on_execute=failing_execute)
    flow = Flow("pipeline", [step], observer=observer)

    with pytest.raises(FlowExecutionError) as exc_info:
        flow.run()

    assert [call[0] for call in observer.calls] == ["on_start", "on_error"]
    assert exc_info.value.step_name == "risky"
    assert isinstance(exc_info.value.original_error, ValueError)


def test_run_calls_observer_hooks_in_step_order_for_multiple_steps(make_step: MakeStep) -> None:
    observer = RecordingFlowObserver()
    step_a = make_step(name="a")
    step_b = make_step(name="b")

    flow = Flow("pipeline", [step_a, step_b], observer=observer)
    flow.run()

    step_names_in_call_order = [call[1] for call in observer.calls]
    assert step_names_in_call_order == ["a", "a", "b", "b"]


def test_run_uses_default_logging_observer_when_none_provided(
    make_step: MakeStep, caplog: pytest.LogCaptureFixture
) -> None:
    step = make_step(name="step")
    flow = Flow("pipeline", [step])

    with caplog.at_level(
        logging.INFO, logger="flowstep.core.observability.flow_observers.logging_flow_observer"
    ):
        flow.run()

    assert any("step" in record.getMessage() for record in caplog.records)
