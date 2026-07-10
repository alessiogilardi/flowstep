"""Step generico che applica una catena di transform (iterabile→iterabile) a un valore
del contesto.
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
    """Applica in catena uno o più transform (iterabile→iterabile) a un valore del contesto.

    Args:
        name: Nome univoco dello step nel flow.
        transforms: Uno o più callable `Iterable → Iterable` applicati in sequenza.
        input_key: Chiave da cui leggere il valore sorgente nel `FlowContext`.
        output_key: Chiave in cui scrivere il risultato nel `FlowContext`.
        data_volume_observer: Observer notificato con gli elementi consumati/prodotti
            al termine dell'esecuzione. Default `LoggingDataVolumeObserver()`.

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
        """Inietta nome, catena di transform, input key, output key e data volume observer.

        Args:
            name: Nome univoco dello step.
            *transforms: Callable applicati in sequenza (zero o più).
            input_key: Chiave sorgente nel contesto.
            output_key: Chiave destinazione nel contesto.
            data_volume_observer: Observer per il conteggio elementi. Default
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
        """Legge `input_key`, applica la catena di transform, scrive in `output_key`
        e notifica il data volume observer con gli elementi consumati/prodotti.

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
        """Richiede `input_key` nel contesto."""
        return {self._input_key}

    def get_produced_keys(self) -> set[str]:
        """Produce `output_key` nel contesto."""
        return {self._output_key}
