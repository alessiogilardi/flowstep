"""Behavior tests for the default LoggingDataVolumeObserver."""

import logging

import pytest
from conftest import MakeStep

from flowstep.core.observability import LoggingDataVolumeObserver

_LOGGER_NAME = "flowstep.core.observability.data_volume_observers.logging_data_volume_observer"


def test_on_processed_logs_info_with_step_name_and_sizes(
    make_step: MakeStep, caplog: pytest.LogCaptureFixture
) -> None:
    step = make_step(name="apply")
    observer = LoggingDataVolumeObserver()

    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        observer.on_processed(step, 3, 5)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.INFO
    message = record.getMessage()
    assert "apply" in message
    assert "3" in message
    assert "5" in message


def test_on_processed_logs_unknown_when_size_is_none(
    make_step: MakeStep, caplog: pytest.LogCaptureFixture
) -> None:
    step = make_step(name="apply")
    observer = LoggingDataVolumeObserver()

    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        observer.on_processed(step, None, None)

    assert len(caplog.records) == 1
    assert "unknown" in caplog.records[0].getMessage()
