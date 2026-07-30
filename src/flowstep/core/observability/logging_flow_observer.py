"""Default FlowObserver implementation backed by stdlib logging."""

import logging

from ..step import Step
from .models import StepProgress

logger = logging.getLogger(__name__)


class LoggingFlowObserver:
    """Default `FlowObserver` that logs step lifecycle events via stdlib `logging`.

    Structurally satisfies the `FlowObserver` Protocol without inheriting from it.
    """

    def on_start(self, step: Step, progress: StepProgress) -> None:
        """Log a DEBUG message when a step starts.

        Args:
            step: The step about to be executed.
            progress: The step's position within the pipeline.
        """
        logger.debug("Step '%s' started (%d/%d)", step.name, progress.index, progress.total)

    def on_end(self, step: Step, duration_ms: float, progress: StepProgress) -> None:
        """Log an INFO message when a step completes successfully.

        Args:
            step: The step that was executed.
            duration_ms: Execution duration in milliseconds.
            progress: The step's position within the pipeline.
        """
        logger.info(
            "Step '%s' completed in %.2f ms (%d/%d)",
            step.name,
            duration_ms,
            progress.index,
            progress.total,
        )

    def on_error(self, step: Step, error: Exception, progress: StepProgress) -> None:
        """Log an ERROR message when a step fails.

        Args:
            step: The step that failed.
            error: The exception raised by the step.
            progress: The step's position within the pipeline.
        """
        logger.error(
            "Step '%s' failed: %s (%d/%d)", step.name, error, progress.index, progress.total
        )
