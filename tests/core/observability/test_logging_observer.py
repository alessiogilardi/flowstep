"""Behavior tests for the default LoggingObserver."""

import logging

import pytest
from conftest import MakeStep

from flowstep.core.observability import LoggingObserver

_LOGGER_NAME = "flowstep.core.observability.logging_observer"


def test_on_start_logs_debug_with_step_name(
    make_step: MakeStep, caplog: pytest.LogCaptureFixture
) -> None:
    step = make_step(name="load")
    observer = LoggingObserver()

    with caplog.at_level(logging.DEBUG, logger=_LOGGER_NAME):
        observer.on_start(step)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.DEBUG
    assert "load" in record.getMessage()


def test_on_end_logs_info_with_step_name_and_duration(
    make_step: MakeStep, caplog: pytest.LogCaptureFixture
) -> None:
    step = make_step(name="load")
    observer = LoggingObserver()

    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        observer.on_end(step, 12.34)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.INFO
    message = record.getMessage()
    assert "load" in message
    assert "12.34" in message


def test_on_error_logs_error_with_step_name_and_message(
    make_step: MakeStep, caplog: pytest.LogCaptureFixture
) -> None:
    step = make_step(name="load")
    observer = LoggingObserver()
    error = ValueError("boom")

    with caplog.at_level(logging.ERROR, logger=_LOGGER_NAME):
        observer.on_error(step, error)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.ERROR
    message = record.getMessage()
    assert "load" in message
    assert "boom" in message
