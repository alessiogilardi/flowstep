"""Abstract base class for pipeline steps."""

from __future__ import annotations

from abc import ABC, abstractmethod
from time import perf_counter
from typing import TYPE_CHECKING, Self

from ..context import FlowContext

if TYPE_CHECKING:
    from ..observability import StepObserver


class Step(ABC):
    """Abstract base class for all pipeline steps.

    Each step must implement the abstract methods to define:
    - The execution logic
    - The keys required from the context
    - The keys produced in the context

    A step can be instrumented on its own, independent of any `Flow`, by attaching
    `StepObserver`s via `add_observer`. These notifications carry no pipeline-wide
    `StepProgress` — unlike `Flow`'s own `FlowObserver` — since a step may run outside a
    pipeline entirely.

    Attributes:
        _name: Identifying name of the step
    """

    def __init__(self, name: str):
        """Initialize the step.

        Args:
            name: Name of the step (must be unique in the pipeline)
        """
        # Deferred import: `core.observability` imports `Step` for its own type hints, so
        # importing it back at module level here would be a real circular import. This is
        # only ever resolved at instantiation time, well after both modules have loaded.
        from ..observability.composite_step_observer import (
            _CompositeStepObserver,  # pyright: ignore[reportPrivateUsage]
        )

        self._name = name
        self._observer = _CompositeStepObserver()

    @property
    def name(self) -> str:
        return self._name

    def add_observer(self, observer: StepObserver) -> Self:
        """Attach an observer notified of this step's own lifecycle.

        Args:
            observer: Observer to add.

        Returns:
            Self to allow method chaining.
        """
        self._observer.add_observer(observer)
        return self

    def __call__(self, context: FlowContext) -> None:
        self._observer.on_start(self)
        start = perf_counter()
        try:
            self.execute(context)
        except Exception as e:
            self._observer.on_error(self, e)
            raise
        else:
            duration_ms = (perf_counter() - start) * 1000
            self._observer.on_end(self, duration_ms)

    @abstractmethod
    def execute(self, context: FlowContext) -> None:
        """Execute the step logic.

        Args:
            context: Shared pipeline context

        Raises:
            Exception: Any exception during execution
        """
        pass

    @abstractmethod
    def get_required_keys(self) -> set[str]:
        """Return the keys required from the context before execution.

        Returns:
            Set of required keys
        """
        pass

    @abstractmethod
    def get_produced_keys(self) -> set[str]:
        """Return the keys produced into the context after execution.

        Returns:
            Set of produced keys
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self._name}')"
