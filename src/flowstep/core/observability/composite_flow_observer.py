"""Private composite observer that fans out lifecycle events to multiple observers."""

from ..step import Step
from .models import StepProgress
from .protocols import FlowObserver


class _CompositeFlowObserver:  # pyright: ignore[reportUnusedClass]
    """Fans out step lifecycle events to a list of observers, in order.

    Structurally satisfies the `FlowObserver` Protocol. Composition of multiple
    observers is an observability concern, so `Flow` only ever calls a single
    `FlowObserver` and stays unaware of how many observers are behind it.

    Observer calls are intentionally not guarded against exceptions: a broken
    observer is a programming error and should surface rather than be swallowed,
    matching the stance already documented on `Flow`.
    """

    def __init__(self, observers: list[FlowObserver]) -> None:
        """Initialize the composite observer.

        Args:
            observers: Observers to fan out to, in call order.
        """
        self._observers = list(observers)

    def on_start(self, step: Step, progress: StepProgress) -> None:
        """Notify every observer that `step` is about to start.

        Args:
            step: The step about to be executed.
            progress: The step's position within the pipeline.
        """
        for observer in self._observers:
            observer.on_start(step, progress)

    def on_end(self, step: Step, duration_ms: float, progress: StepProgress) -> None:
        """Notify every observer that `step` completed successfully.

        Args:
            step: The step that was executed.
            duration_ms: Execution duration in milliseconds.
            progress: The step's position within the pipeline.
        """
        for observer in self._observers:
            observer.on_end(step, duration_ms, progress)

    def on_error(self, step: Step, error: Exception, progress: StepProgress) -> None:
        """Notify every observer that `step` failed.

        Args:
            step: The step that failed.
            error: The exception raised by the step.
            progress: The step's position within the pipeline.
        """
        for observer in self._observers:
            observer.on_error(step, error, progress)
