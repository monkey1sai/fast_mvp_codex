# Codex Code Project

`C:\.codex_code_project` is the root management workspace for multiple AI-assisted code projects.

This repository tracks the shared orchestration layer:
- root AI workspace files in `.workspace/`
- shared lightweight agent prompts in `agents/`
- the managed repository registry in `repos/index.json`
- root-level supervisor tooling such as `codex-supervisor-mvp/`

Implementation work should happen inside the target managed repository.

## Layout

```text
C:\.codex_code_project
  .workspace/
  agents/
  codex-supervisor-mvp/
  repos/
    index.json
    README.md
    jacks_happy_bots/   # independent git repository
  skills/
```

## Managed Repositories

Managed repositories live under `repos/` and keep their own git history and remotes.

Current registry:
- `repos/jacks_happy_bots`

Reference files:
- `repos/index.json`
- `repos/README.md`

## Git Model

The root repository and each managed repository are intentionally separate.

Rules:
- root git tracks the management layer and root utilities
- child repositories under `repos/` keep their own `.git` directories
- root `.gitignore` excludes nested repository contents by default
- pull, merge, and push project code from inside the child repository

## Supervisor

`codex-supervisor-mvp/` is the root-level supervisor project for monitoring and assisting agent-driven workflows.

It belongs to the root management repository because it is cross-project infrastructure, not a feature of `jacks_happy_bots`.

## Workflow

1. Start from the root workspace when routing or managing multiple projects.
2. Enter the target repository for implementation work.
3. Update `repos/index.json` when adding a new managed repository.
4. Keep `.workspace/router.json` aligned with the active managed projects.
