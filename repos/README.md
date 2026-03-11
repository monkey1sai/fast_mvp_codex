# Repos Registry

`repos/` is the canonical container for managed projects under `C:\.codex_code_project`.

## Rules
- Add each managed repository as a direct child of `repos/`.
- Register every project in `repos/index.json`.
- Keep root-level routing in `.workspace/router.json` aligned with `repos/index.json`.
- Do implementation work inside the target repository, not at the management root.

## Current Projects
- `jacks_happy_bots`: SAGA Brain operations repository

## Update Checklist
1. Place or clone the repository under `repos/<project-name>`.
2. Add a project entry to `repos/index.json`.
3. Update `.workspace/router.json` if the project should be routable from the root workspace.
4. Update `.workspace/index.json` only if a new shared root-level index entry is needed.
