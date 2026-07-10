"""Shared fixtures and test doubles for the flowstep test suite."""

from collections.abc import Callable
from typing import Any, Protocol

import pytest

from flowstep.core import FlowContext, Step


class RecordingStep(Step):
    """Step that records calls and lets tests control its contract and behavior."""

    def __init__(
        self,
        name: str,
        required_keys: set[str] | None = None,
        produced_keys: set[str] | None = None,
        on_execute: Callable[[FlowContext], None] | None = None,
    ) -> None:
        super().__init__(name)
        self._required_keys = required_keys or set()
        self._produced_keys = produced_keys or set()
        self._on_execute = on_execute
        self.executed: bool = False

    def execute(self, context: FlowContext) -> None:
        self.executed = True
        if self._on_execute is not None:
            self._on_execute(context)

    def get_required_keys(self) -> set[str]:
        return self._required_keys

    def get_produced_keys(self) -> set[str]:
        return self._produced_keys


class MakeStep(Protocol):
    """Typed factory protocol for building RecordingStep instances in tests."""

    def __call__(
        self,
        name: str = ...,
        required_keys: set[str] | None = ...,
        produced_keys: set[str] | None = ...,
        on_execute: Callable[[FlowContext], None] | None = ...,
    ) -> RecordingStep: ...


@pytest.fixture
def make_step() -> MakeStep:
    """Factory fixture for building RecordingStep instances in tests."""

    def _make_step(
        name: str = "step",
        required_keys: set[str] | None = None,
        produced_keys: set[str] | None = None,
        on_execute: Callable[[FlowContext], None] | None = None,
    ) -> RecordingStep:
        return RecordingStep(name, required_keys, produced_keys, on_execute)

    return _make_step


class RecordingObserver:
    """Observer double that records on_start/on_end/on_error calls as a list of tuples.

    Each entry is `(event, step_name, payload)` where `payload` is `None` for `on_start`,
    the `duration_ms` for `on_end`, and the raised exception for `on_error`. Structurally
    satisfies the `StepObserver` protocol contract without importing it, so this double
    works independently of the observability subpackage.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, Any]] = []

    def on_start(self, step: Step) -> None:
        self.calls.append(("on_start", step.name, None))

    def on_end(self, step: Step, duration_ms: float) -> None:
        self.calls.append(("on_end", step.name, duration_ms))

    def on_error(self, step: Step, error: Exception) -> None:
        self.calls.append(("on_error", step.name, error))


class RecordingDataVolumeObserver:
    """Observer double that records `on_processed` calls as a list of tuples.

    Each entry is `(step_name, input_size, output_size)`. Structurally satisfies the
    `DataVolumeObserver` protocol contract without importing it, so this double works
    independently of the observability subpackage.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, int | None, int | None]] = []

    def on_processed(self, step: Step, input_size: int | None, output_size: int | None) -> None:
        self.calls.append((step.name, input_size, output_size))


@pytest.fixture
def flow_context() -> FlowContext:
    return FlowContext()


@pytest.fixture
def context_data() -> dict[str, Any]:
    return {"key": "value"}
