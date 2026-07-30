"""Pluggable observer protocol for a Flow's pipeline-wide step lifecycle events."""

from typing import Protocol, runtime_checkable

from ...step import Step
from ..models import FlowProgress


@runtime_checkable
class FlowObserver(Protocol):
    """Observes the lifecycle of each step as a `Flow` executes its pipeline.

    Implementations are pluggable monitoring backends (logging, metrics, tracing, ...)
    injected into `Flow` so orchestration stays decoupled from any specific backend.
    Unlike `StepObserver`, these hooks carry `FlowProgress` — pipeline-wide position
    information only `Flow` can know, since a step may run outside any pipeline.
    """

    def on_start(self, step: Step, progress: FlowProgress) -> None:
        """Called immediately before `step.execute()` runs.

        Args:
            step: The step about to be executed.
            progress: The step's position within the pipeline.
        """
        ...

    def on_end(self, step: Step, duration_ms: float, progress: FlowProgress) -> None:
        """Called after `step.execute()` completes successfully.

        Args:
            step: The step that was executed.
            duration_ms: Execution duration in milliseconds.
            progress: The step's position within the pipeline.
        """
        ...

    def on_error(self, step: Step, error: Exception, progress: FlowProgress) -> None:
        """Called when `step.execute()` raises an exception.

        Args:
            step: The step that failed.
            error: The exception raised by the step.
            progress: The step's position within the pipeline.
        """
        ...
