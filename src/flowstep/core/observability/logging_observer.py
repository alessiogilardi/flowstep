"""Default StepObserver implementation backed by stdlib logging."""

import logging

from ..step import Step

logger = logging.getLogger(__name__)


class LoggingObserver:
    """Default `StepObserver` that logs step lifecycle events via stdlib `logging`.

    Structurally satisfies the `StepObserver` Protocol without inheriting from it.
    """

    def on_start(self, step: Step) -> None:
        """Log a DEBUG message when a step starts.

        Args:
            step: The step about to be executed.
        """
        logger.debug("Step '%s' started", step.name)

    def on_end(self, step: Step, duration_ms: float) -> None:
        """Log an INFO message when a step completes successfully.

        Args:
            step: The step that was executed.
            duration_ms: Execution duration in milliseconds.
        """
        logger.info("Step '%s' completed in %.2f ms", step.name, duration_ms)

    def on_error(self, step: Step, error: Exception) -> None:
        """Log an ERROR message when a step fails.

        Args:
            step: The step that failed.
            error: The exception raised by the step.
        """
        logger.error("Step '%s' failed: %s", step.name, error)
