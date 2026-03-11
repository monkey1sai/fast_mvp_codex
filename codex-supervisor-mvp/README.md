# Codex Supervisor MVP

`codex-supervisor-mvp` is the root-level supervisor module for `C:\.codex_code_project`.

It exists at the management root because it is cross-project infrastructure. It is not owned by any single managed repository.

## Responsibilities

- wrap a Codex-like interactive process
- watch stdout for allowlisted prompt patterns
- send safe auto-replies through stdin when a rule matches
- write reproducible session and audit logs to `state/`
- support repo-specific policies stored inside managed repositories

## Module Layout

```text
codex-supervisor-mvp/
  module.json
  supervisor.py
  tests.py
  scripts/
    default-policy.json
    fake_agent.py
    codex-notify.ps1
  state/
```

`state/` is runtime output only and should not be treated as source of truth.

## Policy Model

- Global fallback policy: `scripts/default-policy.json`
- Repo-specific policy: `<managed-repo>/.codex-supervisor/policy.json`
- Repo-specific instructions: `<managed-repo>/.codex-supervisor/AGENTS.md`

The supervisor should only auto-reply to narrow allowlisted prompts. Unknown prompts should be logged, not answered automatically.

## Quick Start

Run the local fake-agent test:

```powershell
python .\tests.py
python .\supervisor.py --policy .\scripts\default-policy.json -- python .\scripts\fake_agent.py
```

Run against a managed repository:

```powershell
Set-Location C:\.codex_code_project\repos\jacks_happy_bots
python C:\.codex_code_project\codex-supervisor-mvp\supervisor.py --policy .\.codex-supervisor\policy.json -- codex --no-alt-screen
```

On Windows, if the command is `codex`, the supervisor will try `codex.cmd` first.

## Notes

- `scripts/codex-notify.ps1` is for event capture, not reliable bidirectional control
- prefer fixing workflow instructions and approval policy before adding more auto-reply rules
- keep repo-specific policies in the managed repository, not in this root module
