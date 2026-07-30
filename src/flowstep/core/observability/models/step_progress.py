"""Value object describing a step's position within a Flow's execution."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StepProgress:
    """Position of a step within the sequential execution of a `Flow`.

    Attributes:
        index: 1-based position of the step in the pipeline (i.e. how many steps,
            including this one, have started).
        total: Total number of steps in the pipeline.
    """

    index: int
    total: int

    @property
    def fraction(self) -> float:
        """Fraction of the pipeline completed once this step finishes, in `[0, 1]`."""
        return self.index / self.total
