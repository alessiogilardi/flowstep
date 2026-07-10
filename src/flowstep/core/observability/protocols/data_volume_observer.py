"""Pluggable observer protocol for step data-volume events."""

from typing import Protocol, runtime_checkable

from ...step import Step


@runtime_checkable
class DataVolumeObserver(Protocol):
    """Observes the volume of data a step consumes and produces.

    Implementations are pluggable monitoring backends (logging, metrics, ...) injected
    into steps that process sized collections, so tracking element counts stays
    decoupled from any specific backend. Scoped to the success path only: a step that
    raises is already reported through `StepObserver.on_error` at the `Flow` level.
    """

    def on_processed(self, step: Step, input_size: int | None, output_size: int | None) -> None:
        """Called after a step finishes transforming its input.

        Args:
            step: The step that ran.
            input_size: Number of elements consumed, or `None` if the input does not
                support `len()`.
            output_size: Number of elements produced, or `None` if the output does not
                support `len()`.
        """
        ...
