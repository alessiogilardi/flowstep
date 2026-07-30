"""Pluggable observer protocol for step lifecycle events."""

from typing import Protocol, runtime_checkable

from ...step import Step
from ..models import StepProgress


@runtime_checkable
class StepObserver(Protocol):
    """Observes the lifecycle of a step's execution.

    Implementations are pluggable monitoring backends (logging, metrics, tracing, ...)
    injected into `Flow` so orchestration stays decoupled from any specific backend.
    """

    def on_start(self, step: Step, progress: StepProgress) -> None:
        """Called immediately before `step.execute()` runs.

        Args:
            step: The step about to be executed.
            progress: The step's position within the pipeline.
        """
        ...

    def on_end(self, step: Step, duration_ms: float, progress: StepProgress) -> None:
        """Called after `step.execute()` completes successfully.

        Args:
            step: The step that was executed.
            duration_ms: Execution duration in milliseconds.
            progress: The step's position within the pipeline.
        """
        ...

    def on_error(self, step: Step, error: Exception, progress: StepProgress) -> None:
        """Called when `step.execute()` raises an exception.

        Args:
            step: The step that failed.
            error: The exception raised by the step.
            progress: The step's position within the pipeline.
        """
        ...
