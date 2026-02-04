# Skills

A public repository of puda skills. This collection includes various skills and capabilities, with more machine skills to be added in the future.

## Overview

This repository contains skills documentation and references for the puda project. Each skill is organized in its own directory with relevant documentation and resources.

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
