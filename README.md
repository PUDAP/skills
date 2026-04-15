# Skills

A public repository of puda skills. This collection includes various skills and capabilities, with more machine skills to be added in the future.

## Overview

This repository contains skills for the Puda project, following the [Agent Skills](https://agentskills.io) standard. Each skill lives in its own directory with a required `SKILL.md` (YAML frontmatter + markdown body) and optional `references/`, `scripts/`, or `assets/`.

### Skill modules

| Skill | Description |
|-------|-------------|
| **puda** | Setup puda project, CLI installation, and project/experiment structure. Use when initializing a Puda project or experiment, or when updating skills. |
| **puda-protocol** | Protocol creation for PUDA. Use when generating or modifying protocols for experiments and discovering machine capabilities. |
| **puda-memory** | Maintains **project.md** as the single source of truth for a project folder. Use after creating/updating protocols, or after running protocols, to record logs, protocol links, and history with timestamps. |
| **puda-database** | Query the puda database using SQL and the puda CLI. Use when users need to inspect schema or run SQL commands. |
| **puda-analysis** | Data analysis using puda with Python. Use when exploring puda database data, running data analysis, creating visualizations, or working with puda data in Python. |
| **puda-edge** | Creating an edge client to integrate any machine into PUDA. Use when scaffolding a new machine edge service, writing a machine driver, or setting up the NATS-based communication layer. |
| **karpathy-guidelines** | Behavioral guidelines to reduce common LLM coding mistakes. Use when writing, reviewing, or refactoring code. |

## CLI Reference

```
puda
├── protocol
│   ├── run                  Run a protocol on machines via NATS
│   └── validate             Validate a protocol JSON file
├── machine
│   ├── list                 Discover machines via heartbeat
│   ├── state <machine_id>   Get the state of a machine
│   ├── reset <machine_id>   Reset a machine
│   └── commands <machine_id> Show available commands
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
