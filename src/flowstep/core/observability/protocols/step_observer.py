"""Pluggable observer protocol for a single step's own lifecycle events."""

from typing import Protocol, runtime_checkable

from ...step import Step


@runtime_checkable
class StepObserver(Protocol):
    """Observes the lifecycle of a single step's execution, independent of any pipeline.

    Implementations are pluggable monitoring backends attached directly to a `Step` via
    `Step.add_observer`, so a step stays instrumentable even when run outside a `Flow`.
    Unlike `FlowObserver`, these hooks carry no `StepProgress` — a step may not belong to
    any pipeline at all.
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
