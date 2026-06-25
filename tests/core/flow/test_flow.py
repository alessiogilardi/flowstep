"""Behavior tests for Flow execution."""

import pytest
from conftest import MakeStep

from flowstep.core import Flow, FlowContext
from flowstep.core.exceptions import FlowExecutionError


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
