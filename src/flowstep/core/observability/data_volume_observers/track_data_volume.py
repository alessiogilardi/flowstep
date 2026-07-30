"""Context manager that measures data volume around a step's transform block."""

from collections.abc import Generator, Sized
from contextlib import contextmanager

from ...context import FlowContext
from ...step import Step
from ..protocols import DataVolumeObserver


def _try_len(value: object) -> int | None:
    """Return `len(value)` if `value` supports it, else `None`.

    Never consumes the value — a lazy iterator that isn't `Sized` is left untouched
    so its elements are still available to the next transform in the chain.
    """
    return len(value) if isinstance(value, Sized) else None


@contextmanager
def track_data_volume(
    observer: DataVolumeObserver,
    step: Step,
    context: FlowContext,
    input_key: str,
    output_key: str,
) -> Generator[None]:
    """Measure input/output element counts around a step's execution block.

    Reads `input_key` from `context` before the wrapped block runs, so the
    pre-block value is used even when `input_key == output_key` (the block may
    overwrite that key before the block completes). Yields control to the wrapped
    block; only if it completes without raising does this read `output_key` back
    from `context` and notify `observer.on_processed`. If the block raises, the
    exception propagates unchanged and the observer is never notified, matching
    `DataVolumeObserver`'s success-only contract (failures are reported via
    `StepObserver.on_error` at the `Flow` level instead).

    Args:
        observer: Observer notified with the measured element counts.
        step: The step being tracked, passed through to `observer.on_processed`.
        context: Shared pipeline context to read `input_key`/`output_key` from.
        input_key: Context key holding the value consumed by the wrapped block.
        output_key: Context key the wrapped block is expected to write to.

    Yields:
        None.
    """
    input_size = _try_len(context.get(input_key))
    yield
    output_size = _try_len(context.get(output_key))
    observer.on_processed(step, input_size, output_size)
