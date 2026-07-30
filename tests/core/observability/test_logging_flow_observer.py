"""Behavior tests for the default LoggingFlowObserver."""

import logging

import pytest
from conftest import MakeStep

from flowstep.core import StepProgress
from flowstep.core.observability import LoggingFlowObserver

_LOGGER_NAME = "flowstep.core.observability.logging_flow_observer"
_PROGRESS = StepProgress(index=2, total=5)


def test_on_start_logs_debug_with_step_name_and_progress(
    make_step: MakeStep, caplog: pytest.LogCaptureFixture
) -> None:
    step = make_step(name="load")
    observer = LoggingFlowObserver()

    with caplog.at_level(logging.DEBUG, logger=_LOGGER_NAME):
        observer.on_start(step, _PROGRESS)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.DEBUG
    message = record.getMessage()
    assert "load" in message
    assert "2/5" in message


def test_on_end_logs_info_with_step_name_duration_and_progress(
    make_step: MakeStep, caplog: pytest.LogCaptureFixture
) -> None:
    step = make_step(name="load")
    observer = LoggingFlowObserver()

    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        observer.on_end(step, 12.34, _PROGRESS)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.INFO
    message = record.getMessage()
    assert "load" in message
    assert "12.34" in message
    assert "2/5" in message


def test_on_error_logs_error_with_step_name_message_and_progress(
    make_step: MakeStep, caplog: pytest.LogCaptureFixture
) -> None:
    step = make_step(name="load")
    observer = LoggingFlowObserver()
    error = ValueError("boom")

    with caplog.at_level(logging.ERROR, logger=_LOGGER_NAME):
        observer.on_error(step, error, _PROGRESS)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.ERROR
    message = record.getMessage()
    assert "load" in message
    assert "boom" in message
    assert "2/5" in message
