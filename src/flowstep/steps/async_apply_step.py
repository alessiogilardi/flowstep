"""Generic step that applies a chain of async transforms under a single event loop.

The async twin of flowstep's ``ApplyStep``: it reads a value from the context, awaits
each async transform in sequence, and writes the result back. It owns the single
``asyncio.run`` for the whole chain, so every awaited transform shares one event loop —
avoiding cross-loop reuse of any client (e.g. a shared ``httpx.AsyncClient``) held by the
transforms. Transforms run strictly in order: transform N+1 starts only after transform N
has fully completed.
"""

import asyncio
from collections.abc import Awaitable, Callable, Iterable
from typing import Any, override

from flowstep.core import DataVolumeObserver

from .apply_step import ApplyStep


class AsyncApplyStep(ApplyStep):
    """Applies one or more async transforms (Iterable → Awaitable[Iterable]) in sequence.

    Args:
        name: Unique step name within the flow.
        *transforms: Async callables applied in order; each awaited to completion before
            the next starts.
        input_key: Context key to read the source value from.
        output_key: Context key to write the result to.
        data_volume_observer: Observer notified with consumed/produced element counts.
            Defaults to ``LoggingDataVolumeObserver()``.
    """

    def __init__(
        self,
        name: str,
        *transforms: Callable[[Iterable[Any]], Awaitable[Iterable[Any]]],
        input_key: str,
        output_key: str,
        data_volume_observer: DataVolumeObserver | None = None,
    ) -> None:
        """Injects name, async transform chain, input/output keys and data volume observer."""
        super().__init__(
            name,
            input_key=input_key,
            output_key=output_key,
            data_volume_observer=data_volume_observer,
        )
        self._transforms = transforms

    @override
    def apply(self, result: Any) -> Any:
        """Applies the transform chain to the result."""
        return asyncio.run(self._apply_chain(result))

    async def _apply_chain(self, result: Iterable[Any]) -> Iterable[Any]:
        """Awaits each transform in sequence; transform N+1 starts only after N completes."""
        for transform in self._transforms:
            result = await transform(result)
        return result
