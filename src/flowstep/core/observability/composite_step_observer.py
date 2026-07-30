"""Private composite observer that fans out a step's own lifecycle events."""

from typing import Self

from ..step import Step
from .protocols import StepObserver


class _CompositeStepObserver:  # pyright: ignore[reportUnusedClass]
    """Fans out a step's own lifecycle events to a list of observers, in order.

    Structurally satisfies the `StepObserver` Protocol. Unlike `_CompositeFlowObserver`,
    which `FlowBuilder` builds once from a fixed list, this composite backs
    `Step.add_observer` directly, so observers can be registered incrementally over the
    step's lifetime.

    Observer calls are intentionally not guarded against exceptions: a broken observer is
    a programming error and should surface rather than be swallowed, matching the stance
    already documented on `Flow`.
    """

    def __init__(self) -> None:
        """Initialize the composite observer with no observers registered."""
        self._observers: list[StepObserver] = []

    def add_observer(self, observer: StepObserver) -> Self:
        """Register an observer to fan out to.

        Args:
            observer: Observer to add.

        Returns:
            Self to allow method chaining.
        """
        self._observers.append(observer)
        return self

    def on_start(self, step: Step) -> None:
        """Notify every observer that `step` is about to start.

        Args:
            step: The step about to be executed.
        """
        for observer in self._observers:
            observer.on_start(step)

    def on_end(self, step: Step, duration_ms: float) -> None:
        """Notify every observer that `step` completed successfully.

        Args:
            step: The step that was executed.
            duration_ms: Execution duration in milliseconds.
        """
        for observer in self._observers:
            observer.on_end(step, duration_ms)

    def on_error(self, step: Step, error: Exception) -> None:
        """Notify every observer that `step` failed.

        Args:
            step: The step that failed.
            error: The exception raised by the step.
        """
        for observer in self._observers:
            observer.on_error(step, error)
