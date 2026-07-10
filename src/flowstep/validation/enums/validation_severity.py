"""Enumerations for the validation system."""

from enum import StrEnum


class ValidationSeverity(StrEnum):
    """Severity level of a validation result.

    Attributes:
        ERROR: Blocking error that prevents pipeline execution
        WARNING: Non-blocking warning
    """

    ERROR = "error"
    WARNING = "warning"
