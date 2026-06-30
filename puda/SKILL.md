---
name: puda
description: Set up the PUDA CLI and initialize projects. Covers CLI installation, dependencies, login, NATS config, skills install/update, and project folder structure. Use when setting up PUDA, initializing a new project, or updating installed skills.
---
## Setup puda

1. **Install CLI**: Ensure `puda` is installed and on your PATH so it can be invoked globally. If missing, download the binary for your platform from the [Puda releases page](https://github.com/PUDAP/puda/releases), install it, and add it to PATH.
2. **Ensure dependencies**: Ensure `python3`, `pip`, and `npx` are available; install them first if missing.
3. **Login**: Ask the user for their username if not already known — do not assume. Log in with `puda login -u <username>`.
4. **Setup NATS servers**: Run `puda config list` to see the current `nats_servers` value. If not set or the user wants to change it, ask for the comma-separated NATS server URLs — do not assume. Set with `puda config set nats_servers <comma-separated-urls>`.
5. **Install skills**: Run `puda skills install` to install agent skills for puda.

## Setup project

Run `puda init` (e.g. `puda init .` or `puda init <folder_name>`).

Only after puda is set up and the project is initialized, proceed with protocol generation, machine commands, or experiment workflows.

## Project Folder Structure

```text
.
├── project.md                        # single source of truth (puda-memory skill)
├── protocols/                        # generated protocol files (puda-protocol skill)
├── puda.config                       # puda config file
└── puda.db                           # puda database file
```

## Updating puda skills

To refresh or update puda skills:

```bash
puda skills update
```
