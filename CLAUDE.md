# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

FlowStep is an early-stage library. The package lives under `src/flowstep/` and is meant to be
imported as `commons.flowstep` per the README examples, but the actual installed package name is
`flowstep` — confirm which import path is correct before relying on README snippets.

## Development commands

Dependency management and tooling use `uv` exclusively (per global Python standards).

```bash
uv sync                  # install runtime + dev dependencies (ruff, pyright, pytest)
uv run pytest -q         # run the full test suite
uv run pytest tests/core/flow/test_flow.py::test_run_executes_steps_in_order  # single test
uv run ruff check .      # lint
uv run ruff check --fix .  # lint with autofix
uv run pyright           # type check
```

`tests/` mirrors the `src/flowstep/` package layout. `tests/conftest.py` defines a shared
`RecordingStep` test double and a `make_step` factory fixture (typed as `MakeStep`) used across
the suite instead of re-declaring `Step` subclasses per test file — import it with
`from conftest import MakeStep` (the `tests` directory is on `pythonpath` via the pytest config,
so this works without `tests/__init__.py` files).

`[tool.pyright]` is set to `typeCheckingMode = "strict"`. Key typing decisions worth noting:
- `flow_validator.py`'s duck-typed custom `validate()` hook is modelled as a `runtime_checkable`
  `_SupportsCustomValidation` Protocol; `isinstance(step, _SupportsCustomValidation)` narrows the
  type before calling `.validate()`.
- `_extract_keys` accepts `getter: Callable[[], object]` (not `set[str]`) so it can defensively
  validate runtime contract violations even from statically-typed `Step` subclasses;
  `cast(set[object], raw_keys)` is used after the `isinstance(raw_keys, set)` guard to give
  pyright a typed iterable.

## Versioning

flowstep uses SemVer (`major.minor.bugfix`), tracked in `pyproject.toml` via
`uv version --bump {major,minor,patch}` (no dynamic/VCS-derived versioning, no
commitizen/semantic-release — there's no CI yet to run that automation against). Baseline is
tagged `v0.1.0`.

Version bumps happen **per qualifying commit**, not at separate release time, driven by the
commit's gitmoji (see the global `commit` skill for the full legend):

| Gitmoji | Meaning | Bump | CHANGELOG category |
|---|---|---|---|
| ✨ | New feature | minor | Added |
| 🐛 / 🩹 / 🚑️ | Bug fix / simple fix / hotfix | patch | Fixed |
| 🔒️ | Security fix | patch | Security |
| everything else (♻️ 📝 ✅ 🔧 📦 💄 ⚡️ 🔥 🚚 🏗️ 🎉 ⏪️ 💡 🏷️ 🌱) | internal/non-behavioral | none | — |

- **Pre-1.0 caveat**: while the version is `0.x.y`, SemVer permits breaking changes within minor
  bumps. A major bump (or the `1.0.0` transition) is never inferred automatically from a
  gitmoji — only when the user explicitly asks for it, since the gitmoji legend has no
  dedicated "breaking change" marker.
- **Edge cases** (🔥 removing public API, ⚡️ changing observable behavior): flag for manual
  judgment rather than auto-bumping — not reliably classifiable from the emoji alone.
- **Process**: before staging a commit in this repo, check whether its gitmoji triggers a bump.
  - If yes: run `uv version --bump <level>` (updates `pyproject.toml` + `uv.lock`), prepend a
    `## [X.Y.Z] - <date>` entry to `CHANGELOG.md` under the matching category with the commit
    subject (minus emoji, verbatim — CHANGELOG entries are mechanically derived, never
    freehand-summarized) as the bullet, then stage `pyproject.toml`, `uv.lock`, and
    `CHANGELOG.md` alongside the code change in the **same** commit — it's metadata about the
    same logical change, not a separate one.
  - If no: commit as usual, no version/changelog changes.
- **Tags mark releases, not commits**: `vX.Y.Z` tags (and pushing them) are only created when
  the user explicitly asks for a release — never automatically per commit.

## Architecture

FlowStep is a sequential pipeline (ETL-style) execution framework built around four core
abstractions that live in `src/flowstep/core/`:

- **`Step`** (`core/step/step.py`) — abstract base class for a unit of pipeline work. Subclasses
  implement `execute(context)`, `get_required_keys()`, and `get_produced_keys()`. The required/
  produced key declarations are not enforced at execution time — they exist purely as a contract
  consumed by `FlowValidator` for static analysis before running.
- **`FlowContext`** (`core/context/flow_context.py`) — a typed key/value bag passed between steps.
  `get()` raises `KeyError` on a missing key (no silent `None`); `has()` should be used for
  existence checks.
- **`Flow`** (`core/flow/flow.py`) — executes a list of `Step`s sequentially against a single
  shared `FlowContext`. Any exception raised inside a step's `execute()` is caught and re-raised
  wrapped as `FlowExecutionError(step_name, original_error)` — callers should catch
  `FlowExecutionError` and inspect `.step_name`/`.original_error`, not the raw exception.
- **`FlowBuilder`** (`builder/flow_builder.py`) — fluent construction (`add_step().add_step().build()`).
  `build(validate=True, initial_context=..., initial_context_model=...)` runs `FlowValidator`
  before returning the `Flow`, raising `FlowValidationError` if any ERROR-level finding exists.

### Validation subsystem (`src/flowstep/validation/`)

Validation is decoupled from execution and is opt-in via `FlowBuilder.build(validate=True)`.
`FlowValidator` performs static analysis over the declared `get_required_keys()` /
`get_produced_keys()` contracts without running any step:

- Tracks `available_keys` as it walks the step list, accumulating each step's produced keys.
- A step's required key not yet in `available_keys` is a WARNING (`validate_structure`, no
  initial context known) or escalated to an ERROR if it's also absent from explicit
  `initial_keys` (`validate_with_context`, used when an initial context is supplied).
- Duplicate step names, non-`set[str]` returns from `get_required_keys`/`get_produced_keys`, and
  exceptions raised by those methods are all reported as ERRORs rather than raised directly —
  validation always returns a `FlowValidationReport` rather than throwing, except via
  `FlowValidationError` at the `FlowBuilder.build()` boundary.
- Steps may optionally implement a custom `validate()` method (duck-typed, not part of the `Step`
  ABC) returning a `StepValidationResult`, an iterable of them, or `None`; `FlowValidator` picks
  this up automatically via `_run_custom_validation`.
- `FlowValidationReport` aggregates `StepValidationResult` entries and tracks
  `required_input_keys` — the set of keys the pipeline needs from its initial context, computed
  during structural validation regardless of whether an initial context was supplied.

### Exception hierarchy

Both `core/exceptions/_base_flow_error.py` (`BaseFlowError`) and the validation-specific
`FlowValidationError` inherit from the same base, but live in separate subpackages
(`core/exceptions/` vs `validation/exceptions/`) — execution errors are a `core` concern,
validation errors are a `validation` concern. When adding a new exception, place it under
whichever subpackage owns the failure mode, not a shared top-level `exceptions/`.

### Package re-export pattern

Every subpackage (`core`, `builder`, `validation`, and their nested folders) re-exports its public
surface through `__init__.py` with an explicit `__all__`. The top-level `src/flowstep/__init__.py`
re-exports the full public API (`FlowBuilder`, `Step`, `Flow`, `FlowContext`,
`FlowExecutionError`, validation types). When adding new public types, update both the
subpackage's `__init__.py` and, if it's part of the top-level public API, `flowstep/__init__.py`.

### Documentation language

All documentation, docstrings, comments, and any other generated text added to this
project must be written exclusively in English — no exceptions, regardless of the
language used in the conversation.
