"""Behavior tests for the Step contract."""

from conftest import MakeStep

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
