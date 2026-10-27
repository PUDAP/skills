# Skills

A public repository of puda skills. This collection includes various skills and capabilities, with more machine skills to be added in the future.

## Overview

This repository contains skills for the Puda project, following the [Agent Skills](https://agentskills.io) standard. Each skill lives in its own directory with a required `SKILL.md` (YAML frontmatter + markdown body) and optional `references/`, `scripts/`, or `assets/`.

### Skill modules

| Skill | Description |
|-------|-------------|
| [puda](puda/SKILL.md) | CLI/project setup, profiles, machine inspection, telemetry, clocks, and cameras. |
| [puda-protocol](puda-protocol/SKILL.md) | Protocol creation, validation, execution, and command safety. |
| [puda-memory](puda-memory/SKILL.md) | Project records, protocol links, and timestamped run history. |
| [puda-database](puda-database/SKILL.md) | Schema inspection and SQL through the PUDA CLI. |
| [puda-data](puda-data/SKILL.md) | Extraction, analysis, provenance hashes, exports, plots, experiment reports, and device adapters. |
| [puda-edge](puda-edge/SKILL.md) | Python SDK/API or GUI edge drivers and remote updates. |
| [puda-manual-ui](puda-manual-ui/SKILL.md) | Streamlit operator dashboards using CLI manual sessions. |
| [puda-deployment](puda-deployment/SKILL.md) | Host-to-labware commissioning, troubleshooting, and deployment records. |

### Progressive discovery

The [Agent Skills specification](https://agentskills.io/specification) separates discovery from task instructions and supporting resources:

1. At startup, a compatible agent reads only each skill's `name` and `description`.
2. When a task matches, it reads that skill's `SKILL.md` for the workflow, essential constraints, and resource links.
3. It reads only the linked references needed for the current operation, or executes the relevant bundled scripts. Do not preload every reference or every skill.

For example, a telemetry inspection loads `puda/SKILL.md` and `puda/references/cli-profiles-and-telemetry.md`; it does not need camera, clock, or setup instructions. Short skills such as `puda-memory` stay self-contained.

Skill packaging enables this loading pattern; the agent client controls what it actually loads. Keep descriptions concise, keep detailed examples and task-specific procedures in focused references, and link those references directly from `SKILL.md`. Preserve safety and lifecycle constraints in the entrypoint. Keep entrypoints below the specification's recommended 500 lines / 5,000 tokens.

### Validate skill packages

Use the specification's reference validator (requires [uv](https://docs.astral.sh/uv/)):

```bash
uv tool install 'git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref'
for skill in */SKILL.md; do
  skills-ref validate "${skill%/SKILL.md}" || exit 1
done
```

Also check that relative resource links resolve and that each reference can be selected from its entrypoint without loading unrelated guides. The validator checks format, not instruction quality.

## CLI Reference

```
puda
├── protocol
│   ├── run                  Run a protocol on machines via NATS
│   └── validate             Validate a protocol JSON file
├── machine
│   ├── list                 Discover machines via ping (description, livestream_count)
│   ├── state <machine_id>   Get the state of a machine
│   ├── reset <machine_id>   Reset a machine
│   └── commands <machine_id> Show available commands
├── livestream
│   ├── add                  Register host + stream name and attach machines
│   ├── list                 List fleet livestreams [--hosts] [--machines]
│   ├── rm                   Remove a livestream
│   ├── attach               Attach machines to a livestream
│   └── detach               Detach machines from a livestream
├── login                    Log in to a PUDA account
├── logout                   Log out of a PUDA account
├── config
│   ├── list                 List configuration values
│   └── edit                 Edit configuration in default editor
├── init [path]              Initialize a new PUDA project
├── skills
│   ├── install              Install agent skills
│   └── update               Update agent skills
└── db
    ├── exec [sql]           Execute SQL queries on the database
    └── schema               Display the database schema
```

## Installing skills with the PUDA CLI

Run these from a PUDA project directory (after `puda init` if you are starting fresh). They install the configured agent skills

**Install** — first-time setup or whenever you want a full install and sync from the configured skill source:

```bash
puda skills install
```

**Update** — refresh skills when upstream changes:

```bash
puda skills update
```

## Developing and testing skills

To try skills from a branch or a local clone before they land on `main`, use the CLI (`npx skills add`).

**GitHub branch** — substitute your branch name for `<branch_name>` (example: `feature/new-machine-skill`):

```bash
npx skills add https://github.com/PUDAP/skills/tree/<branch_name> -y
```

**Local directory** — path to a skills repo checkout or any folder that contains skill packages (each with a `SKILL.md`):

```bash
npx skills add ./my-local-skills -y
```

## References

- [vercel-labs/skills](https://github.com/vercel-labs/skills)
- [skills.sh](https://skills.sh/)
- [andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)
