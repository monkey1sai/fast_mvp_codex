# Multi-Project AI Workspace

This workspace is the management layer for multiple projects under `C:\.codex_code_project`.

Current development direction: prioritize shipping production-usable MVPs quickly.
Default model strategy: use `gpt-5.4` for planning and reasoning, and use `gpt-5.3-code` for code generation and implementation tasks.

Use this root when the task is about:
- choosing or routing between projects
- managing shared agent conventions
- coordinating repo-level workflows
- keeping lightweight cross-project context

Prefer entering the target repository for implementation work. Keep the root workspace small and focused on orchestration.

## Managed Paths
- `repos/jacks_happy_bots`: existing repository with its own repo-local workspace
- `repos/`: reserved for additional managed repositories
- `agents/`: shared role prompts for planning, coding, review, and testing
- `skills/`: root-level reusable skills if you decide to add them later

## Operating Rules
- Do not assume one project represents the whole workspace.
- Route to the closest relevant repository before code changes.
- Keep shared context compact to reduce token cost.
- Avoid duplicating project-local documents at the root unless they are truly cross-project.
- Prefer the smallest deployable slice over broad platform work.
- Delay abstraction, automation, and optimization until they unblock delivery.
- Favor defaults, managed services, and simple workflows when they reduce time to production.
- Use `gpt-5.4` when the task is primarily planning, analysis, routing, or decision-making.
- Use `gpt-5.3-code` when the task is primarily code editing, implementation, or patch generation.
