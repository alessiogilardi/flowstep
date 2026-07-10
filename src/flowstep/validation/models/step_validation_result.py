"""Validation result."""

from dataclasses import dataclass
from typing import Any

from ..enums import ValidationSeverity


@dataclass(frozen=True)
class StepValidationResult:
    """Result of a single validation.

    Attributes:
        severity: Severity level of the result
        message: Description of the problem or warning
        step_name: Name of the step that generated the result
        context_key: Context key involved (optional)
    """

    severity: ValidationSeverity
    message: str
    step_name: str
    context_key: str | None = None

    def is_error(self) -> bool:
        """Checks whether the result is a blocking error.

        Returns:
            True if it is an error, False otherwise
        """
        return self.severity is ValidationSeverity.ERROR

    def is_warning(self) -> bool:
        """Checks whether the result is a warning.

        Returns:
            True if it is a warning, False otherwise
        """
        return self.severity is ValidationSeverity.WARNING

    def to_dict(self) -> dict[str, Any]:
        """Serializes the result into a dictionary.

        Returns:
            Dictionary with the result data
        """
        return {
            "severity": self.severity.value,
            "message": self.message,
            "step_name": self.step_name,
            "context_key": self.context_key,
        }
