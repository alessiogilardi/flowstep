"""Pipeline orchestrator."""

from time import perf_counter
from typing import Any

from ..context import FlowContext
from ..exceptions import FlowExecutionError
from ..observability import FlowObserver, LoggingFlowObserver, StepProgress
from ..step import Step


class Flow:
    """Orchestrator for the sequence of steps.

    Manages the sequential execution of steps.

    Attributes:
        name: Name of the pipeline.
    """

    __context: FlowContext | None

    def __init__(
        self,
        name: str,
        steps: list[Step],
        observer: FlowObserver | None = None,
    ) -> None:
        """Initialize the pipeline.

        Args:
            name: Name of the pipeline.
            steps: List of steps to execute sequentially.
            observer: Step lifecycle observer. Defaults to `LoggingFlowObserver()`.
        """
        self.name = name
        self._steps = list(steps)
        self._observer: FlowObserver = observer or LoggingFlowObserver()

    @property
    def _context(self) -> FlowContext:
        if self.__context is None:
            self.__context = FlowContext()
        return self.__context

    @_context.setter
    def _context(self, new_context: FlowContext | dict[str, Any] | None) -> None:
        if not new_context:
            self.__context = FlowContext()
        elif isinstance(new_context, FlowContext):
            self.__context = new_context
        else:
            self.__context = FlowContext(new_context)

    def run(self, initial_context: FlowContext | dict[str, Any] | None = None) -> FlowContext:
        """Execute the pipeline sequentially.

        Args:
            initial_context: Initial data to seed into the context.

        Returns:
            Final context with all produced data.

        Raises:
            FlowExecutionError: If a step raises during execution.
        """
        self._context = initial_context
        total_steps = len(self._steps)
        for index, step in enumerate(self._steps, start=1):
            self.__execute_step(step, StepProgress(index=index, total=total_steps))
        return self._context

    def get_steps(self) -> list[Step]:
        """Return a copy of the steps list.

        Returns:
            Copy of the steps list.
        """
        return self._steps.copy()

    def __repr__(self) -> str:
        return f"Flow(name='{self.name}', steps={len(self._steps)})"

    def __execute_step(self, step: Step, progress: StepProgress) -> None:
        self._observer.on_start(step, progress)
        start = perf_counter()
        try:
            step(self._context)
        except Exception as e:
            self._observer.on_error(step, e, progress)
            raise FlowExecutionError(step.name, e) from e
        else:
            self._observer.on_end(step, (perf_counter() - start) * 1000, progress)
