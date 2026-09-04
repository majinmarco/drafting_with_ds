# Workspace rules

- **All lessons and code exercises in this workspace are implemented as marimo notebooks** (`.py`, marimo app format), not plain scripts and not HTML-with-separate-scripts. marimo is preferred over ipynb: reactive, plain-Python file format, git-friendly, easy for an LLM to edit.
  - Include PEP 723 inline dependencies (`# /// script`) so notebooks run with `uvx marimo edit --sandbox <file>` and validate with `uv run <file>`.
  - Narrative goes in `mo.md` cells (`hide_code=True`); quizzes use `mo.ui.radio` with a reactive feedback cell; exercises are `None`-placeholder TODO cells with reactive check cells that grade automatically; solutions go in a `mo.accordion` at the bottom.
  - After writing/editing a notebook, run `marimo check --fix <file>` then verify with `uv run <file>`.
- Reference documents (`reference/*.html`) stay as print-friendly HTML per the teach-skill format.
- No system pandas here — everything runs through `uv` with inline dependencies.
- This is a teaching workspace for the `/teach` skill: see `MISSION.md`, `NOTES.md`, `RESOURCES.md`.
