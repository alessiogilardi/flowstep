"""Behavior tests for FlowBuilder."""

import pytest
from conftest import MakeStep

from flowstep.builder import FlowBuilder
from flowstep.core import Flow
from flowstep.validation.exceptions import FlowValidationError


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

    flow = FlowBuilder("pipeline").add_step(step).build(
        validate=True, initial_context={"input": "value"}
    )

    assert isinstance(flow, Flow)
