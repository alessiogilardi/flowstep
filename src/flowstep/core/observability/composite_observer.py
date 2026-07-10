
"""Private composite observer that fans out lifecycle events to multiple observers."""

from ..step import Step
from .step_observer import StepObserver


class _CompositeObserver:  # pyright: ignore[reportUnusedClass]
    """Fans out step lifecycle events to a list of observers, in order.

    Structurally satisfies the `StepObserver` Protocol. Composition of multiple
    observers is an observability concern, so `Flow` only ever calls a single
    `StepObserver` and stays unaware of how many observers are behind it.

    Observer calls are intentionally not guarded against exceptions: a broken
    observer is a programming error and should surface rather than be swallowed,
    matching the stance already documented on `Flow`.
    """

    def __init__(self, observers: list[StepObserver]) -> None:
        """Initialize the composite observer.

        Args:
            observers: Observers to fan out to, in call order.
        """
        self._observers = list(observers)

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
