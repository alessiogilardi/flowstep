# Changelog

All notable changes to this project are documented in this file. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [SemVer](https://semver.org/).

## [Unreleased]

## [0.4.0] - 2026-07-30

### Added

- Split FlowObserver from StepObserver; add Step.add_observer

## [0.3.0] - 2026-07-30

### Added

- Propagate step index and total to observer hooks

## [0.2.0] - 2026-07-30

### Added

- Add AsyncApplyStep for async transform chains

## [0.1.0] - 2026-07-10

### Added

- Add core abstractions: Step, FlowContext, Flow, exceptions
- Add FlowBuilder with fluent API and optional validation
- Add validation subsystem: FlowValidator, report, and severity
- Add pluggable step observability with FlowBuilder integration
- Add ApplyStep for chained context transforms
