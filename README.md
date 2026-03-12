# Skills

A public repository of puda skills. This collection includes various skills and capabilities, with more machine skills to be added in the future.

## Overview

This repository contains skills for the Puda project, following the [Agent Skills](https://agentskills.io) standard. Each skill lives in its own directory with a required `SKILL.md` (YAML frontmatter + markdown body) and optional `references/`, `scripts/`, or `assets/`.

### Skill modules

| Skill | Description |
|-------|-------------|
| **puda** | Setup puda project, CLI installation, and project/experiment structure. Use when initializing a Puda project or experiment, or when updating skills. |
| **puda-protocol** | Protocol creation for PUDA. Use when generating or modifying protocols for experiments and discovering machine capabilities. |
| **puda-memory** | Maintains **experiment.md** as the single source of truth for an experiment. Use after creating/updating protocols, or after running protocols, to record logs, protocol links, and history with timestamps. |
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
│   ├── install              Install and sync agent skills
│   └── update               Update agent skills and sync AGENTS.md
└── db
    ├── exec [sql]           Execute SQL queries on the database
    └── schema               Display the database schema
```

## Installing Skills

Install and sync agent skills using the puda CLI:

```bash
puda skills install
```

To update skills and sync your `AGENTS.md`:

```bash
puda skills update
```

## Reference for Writing New Skills

When creating new skills, refer to the following guide:

- [OpenSkills Example](https://github.com/numman-ali/openskills/blob/main/examples/my-first-skill/SKILL.md)
- [andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)
