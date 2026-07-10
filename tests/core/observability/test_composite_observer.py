"""Behavior tests for the private _CompositeObserver fan-out."""

from conftest import MakeStep, RecordingObserver

from flowstep.core.observability.composite_observer import (
    _CompositeObserver,  # pyright: ignore[reportPrivateUsage]
)


def test_on_start_fans_out_to_all_observers(make_step: MakeStep) -> None:
    first = RecordingObserver()
    second = RecordingObserver()
    step = make_step(name="step")

    composite = _CompositeObserver([first, second])
    composite.on_start(step)

    assert first.calls == [("on_start", "step", None)]
    assert second.calls == [("on_start", "step", None)]


def test_on_end_fans_out_to_all_observers(make_step: MakeStep) -> None:
    first = RecordingObserver()
    second = RecordingObserver()
    step = make_step(name="step")

    composite = _CompositeObserver([first, second])
    composite.on_end(step, 12.5)

    assert first.calls == [("on_end", "step", 12.5)]
    assert second.calls == [("on_end", "step", 12.5)]


def test_on_error_fans_out_to_all_observers(make_step: MakeStep) -> None:
    first = RecordingObserver()
    second = RecordingObserver()
    step = make_step(name="step")
    error = ValueError("boom")

    composite = _CompositeObserver([first, second])
    composite.on_error(step, error)

    assert first.calls == [("on_error", "step", error)]
    assert second.calls == [("on_error", "step", error)]


def test_fans_out_in_list_order(make_step: MakeStep) -> None:
    call_order: list[str] = []

    class OrderTrackingObserver:
        def __init__(self, label: str) -> None:
            self._label = label

        def on_start(self, step: object) -> None:
            call_order.append(self._label)

        def on_end(self, step: object, duration_ms: float) -> None:
            pass

        def on_error(self, step: object, error: Exception) -> None:
            pass

    first = OrderTrackingObserver("first")
    second = OrderTrackingObserver("second")
    step = make_step(name="step")

    composite = _CompositeObserver([first, second])
    composite.on_start(step)

    assert call_order == ["first", "second"]


def test_empty_observer_list_is_a_no_op(make_step: MakeStep) -> None:
    step = make_step(name="step")
    composite = _CompositeObserver([])

    composite.on_start(step)
    composite.on_end(step, 1.0)
    composite.on_error(step, ValueError("boom"))
