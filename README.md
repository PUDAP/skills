# Skills

A public repository of puda skills. This collection includes various skills and capabilities, with more machine skills to be added in the future.

## Overview

This repository contains skills for the Puda project, following the [Agent Skills](https://agentskills.io) standard. Each skill lives in its own directory with a required `SKILL.md` (YAML frontmatter + markdown body) and optional `references/`, `scripts/`, or `assets/`.

### Skill modules

| Skill | Description |
|-------|-------------|
| **puda-setup** | Ensures the Puda CLI is installed and configured; use before any puda commands or when initializing a project. |
| **puda-protocol-gen** | Machine discovery and JSON protocol creation. Use puda machine commands for capabilities; generate protocols; **must** call puda-memory after creating/updating a protocol file. |
| **puda-memory** | Keeps **experiment.md** as the source of truth (logs, protocol links, history with timestamps). Use after creating/updating protocols or after runs. |
| **puda-cli** | Using the puda CLI: machine operations, protocol validation/send, database queries, First and Biologic machine references. |
| **puda-experiment** | Experiment folder layout, tracking, and workflow; references protocol generation and experiment memory. |
| **karpathy-guidelines** | Coding and workflow guidelines. |

## Installing Skills

Skills in this repository can be installed using [OpenSkills](https://github.com/numman-ali/openskills), a universal skills loader for AI coding agents.

### Install from This Repository

```bash
npx openskills install PUDAP/skills
```

### Install from a Local Path

If you've cloned this repository locally:

```bash
npx openskills install ./path/to/skills
```

### Sync Skills to AGENTS.md

After installing skills, sync them to your `AGENTS.md` file:

```bash
npx openskills sync
```

This will update your `AGENTS.md` with the available skills, making them accessible to your AI coding agent.

### Additional Options

- Install globally: `npx openskills install <source> --global`
- Use universal mode (for multi-agent setups): `npx openskills install <source> --universal`
- List installed skills: `npx openskills list`
- Read a specific skill: `npx openskills read <skill-name>`

For more information, see the [OpenSkills documentation](https://github.com/numman-ali/openskills/blob/main/README.md).

## Reference for Writing New Skills

When creating new skills, refer to the following guide:

- [OpenSkills Example](https://github.com/numman-ali/openskills/blob/main/examples/my-first-skill/SKILL.md)
- [andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)
