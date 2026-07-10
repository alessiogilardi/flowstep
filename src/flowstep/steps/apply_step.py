"""Generic step that applies a chain of transforms (iterable→iterable) to a value in the
context.
"""

from collections.abc import Callable, Iterable
from typing import Any

from flowstep.core import (
    DataVolumeObserver,
    FlowContext,
    LoggingDataVolumeObserver,
    Step,
    track_data_volume,
)


class ApplyStep(Step):
    """Applies one or more transforms (iterable→iterable) to a context value, in sequence.

    Args:
        name: Unique name of the step within the flow.
        transforms: One or more `Iterable → Iterable` callables applied in sequence.
        input_key: Key to read the source value from in the `FlowContext`.
        output_key: Key to write the result to in the `FlowContext`.
        data_volume_observer: Observer notified with the elements consumed/produced
            at the end of execution. Defaults to `LoggingDataVolumeObserver()`.

    Example::

        step = ApplyStep(
            "clean",
            ForEach(ArticleCleaner()),
            input_key=context_keys.PARSED_ARTICLES,
            output_key=context_keys.CLEANED_ARTICLES,
        )
    """

    def __init__(
        self,
        name: str,
        *transforms: Callable[[Iterable[Any]], Iterable[Any]],
        input_key: str,
        output_key: str,
        data_volume_observer: DataVolumeObserver | None = None,
    ) -> None:
        """Injects name, transform chain, input key, output key, and data volume observer.

        Args:
            name: Unique name of the step.
            *transforms: Callables applied in sequence (zero or more).
            input_key: Source key in the context.
            output_key: Destination key in the context.
            data_volume_observer: Observer for element counting. Defaults to
                `LoggingDataVolumeObserver()`.
        """
        super().__init__(name)
        self._transforms = transforms
        self._input_key = input_key
        self._output_key = output_key
        self._data_volume_observer: DataVolumeObserver = (
            data_volume_observer or LoggingDataVolumeObserver()
        )

    def execute(self, context: FlowContext) -> None:
        """Reads `input_key`, applies the transform chain, writes to `output_key`,
        and notifies the data volume observer with the elements consumed/produced.

        Args:
            context: Shared pipeline context.
        """
        with track_data_volume(
            self._data_volume_observer, self, context, self._input_key, self._output_key
        ):
            result: Any = context.get(self._input_key)
            for transform in self._transforms:
                result = transform(result)
            context.put(self._output_key, result)

    def get_required_keys(self) -> set[str]:
        """Requires `input_key` in the context."""
        return {self._input_key}

    def get_produced_keys(self) -> set[str]:
        """Produces `output_key` in the context."""
        return {self._output_key}
