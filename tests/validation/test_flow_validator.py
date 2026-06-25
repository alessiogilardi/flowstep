"""Behavior tests for FlowValidator."""

from conftest import MakeStep

from flowstep.core import Flow
from flowstep.validation import ValidationSeverity
from flowstep.validation.flow_validator import FlowValidator


def test_validate_structure_has_no_issues_for_satisfied_contract(make_step: MakeStep) -> None:
    step = make_step(name="load", required_keys=set(), produced_keys={"raw_data"})

    report = FlowValidator().validate_structure(Flow("pipeline", [step]))

    assert report.has_errors() is False
    assert report.has_warnings() is False


def test_validate_structure_warns_on_unsatisfied_required_key(make_step: MakeStep) -> None:
    step = make_step(name="transform", required_keys={"raw_data"})

    report = FlowValidator().validate_structure(Flow("pipeline", [step]))

    assert report.has_warnings() is True
    assert report.required_input_keys == {"raw_data"}


def test_validate_structure_errors_on_duplicate_step_names(make_step: MakeStep) -> None:
    step_a = make_step(name="dup")
    step_b = make_step(name="dup")

    report = FlowValidator().validate_structure(Flow("pipeline", [step_a, step_b]))

    errors = report.get_errors()
    assert any("Duplicate step name" in e.message for e in errors)


def test_validate_structure_warns_on_overwritten_key(make_step: MakeStep) -> None:
    step_a = make_step(name="a", produced_keys={"shared"})
    step_b = make_step(name="b", produced_keys={"shared"})

    report = FlowValidator().validate_structure(Flow("pipeline", [step_a, step_b]))

    warnings = report.get_warnings()
    assert any(w.context_key == "shared" for w in warnings)


def test_validate_structure_errors_when_required_keys_not_a_set(make_step: MakeStep) -> None:
    step = make_step(name="step")
    step.get_required_keys = lambda: ["not", "a", "set"]  # type: ignore[method-assign]

    report = FlowValidator().validate_structure(Flow("pipeline", [step]))

    assert report.has_errors() is True


def test_validate_with_context_errors_when_key_missing_from_initial_context(
    make_step: MakeStep,
) -> None:
    step = make_step(name="transform", required_keys={"raw_data"})

    report = FlowValidator().validate_with_context(Flow("pipeline", [step]), initial_keys=set())

    errors = report.get_errors()
    assert any(e.context_key == "raw_data" for e in errors)


def test_validate_with_context_passes_when_key_present_in_initial_context(
    make_step: MakeStep,
) -> None:
    step = make_step(name="transform", required_keys={"raw_data"})

    report = FlowValidator().validate_with_context(
        Flow("pipeline", [step]), initial_keys={"raw_data"}
    )

    assert report.has_errors() is False


def test_custom_validate_result_is_collected(make_step: MakeStep) -> None:
    from flowstep.validation.models import StepValidationResult

    step = make_step(name="step")
    step.validate = lambda: StepValidationResult(  # type: ignore[attr-defined]
        severity=ValidationSeverity.WARNING,
        message="custom warning",
        step_name="step",
    )

    report = FlowValidator().validate_structure(Flow("pipeline", [step]))

    assert any(w.message == "custom warning" for w in report.get_warnings())
