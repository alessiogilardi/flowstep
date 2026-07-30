"""Behavior tests for the FlowProgress value object."""

from flowstep.core import FlowProgress


def test_fraction_is_index_over_total() -> None:
    progress = FlowProgress(index=2, total=5)

    assert progress.fraction == 0.4


def test_fraction_is_one_on_last_step() -> None:
    progress = FlowProgress(index=3, total=3)

    assert progress.fraction == 1.0
