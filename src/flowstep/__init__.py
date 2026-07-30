"""FlowStep — Data processing pipeline management system.

Example:
    >>> from commons.flowstep import Flow, Step, FlowContext, FlowBuilder
    >>>
    >>> pipeline = (FlowBuilder("my_pipeline")
    ...     .add_step(LoadDataStep())
    ...     .add_step(ProcessDataStep())
    ...     .build())
    >>>
    >>> result = pipeline.run({"input": "data"})
"""

from .builder import FlowBuilder
from .core import (
    DataVolumeObserver,
    Flow,
    FlowContext,
    FlowObserver,
    FlowProgress,
    LoggingDataVolumeObserver,
    LoggingFlowObserver,
    LoggingStepObserver,
    Step,
    StepObserver,
    track_data_volume,
)
from .core.exceptions import FlowExecutionError
from .validation import (
    FlowValidationError,
    FlowValidationReport,
    FlowValidator,
    StepValidationResult,
    ValidationSeverity,
)

__all__ = [
    "FlowBuilder",
    "Step",
    "Flow",
    "FlowContext",
    "FlowExecutionError",
    "FlowObserver",
    "LoggingFlowObserver",
    "StepObserver",
    "LoggingStepObserver",
    "DataVolumeObserver",
    "LoggingDataVolumeObserver",
    "FlowProgress",
    "track_data_volume",
    "ValidationSeverity",
    "StepValidationResult",
    "FlowValidationReport",
    "FlowValidator",
    "FlowValidationError",
]
