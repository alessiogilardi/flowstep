"""Default DataVolumeObserver implementation backed by stdlib logging."""

import logging

from ...step import Step

logger = logging.getLogger(__name__)


class LoggingDataVolumeObserver:
    """Default `DataVolumeObserver` that logs consumed/produced element counts.

    Structurally satisfies the `DataVolumeObserver` Protocol without inheriting from it.
    """

    def on_processed(self, step: Step, input_size: int | None, output_size: int | None) -> None:
        """Log an INFO message with the step's consumed/produced element counts.

        Args:
            step: The step that ran.
            input_size: Number of elements consumed, or `None` if unknown.
            output_size: Number of elements produced, or `None` if unknown.
        """
        logger.info(
            "Step '%s' consumed %s element(s), produced %s element(s)",
            step.name,
            input_size if input_size is not None else "unknown",
            output_size if output_size is not None else "unknown",
        )
