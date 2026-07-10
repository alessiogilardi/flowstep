"""Pluggable observer protocol for step lifecycle events."""

from typing import Protocol, runtime_checkable

from ..step import Step


@runtime_checkable
class StepObserver(Protocol):
    """Observes the lifecycle of a step's execution.

    Implementations are pluggable monitoring backends (logging, metrics, tracing, ...)
    injected into `Flow` so orchestration stays decoupled from any specific backend.
    """

    def on_start(self, step: Step) -> None:
        """Called immediately before `step.execute()` runs.

        Args:
            step: The step about to be executed.
        """
        ...

    def on_end(self, step: Step, duration_ms: float) -> None:
        """Called after `step.execute()` completes successfully.

        Args:
            step: The step that was executed.
            duration_ms: Execution duration in milliseconds.
        """
        ...

    def on_error(self, step: Step, error: Exception) -> None:
        """Called when `step.execute()` raises an exception.

        Args:
            step: The step that failed.
            error: The exception raised by the step.
        """
        ...
