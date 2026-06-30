---
name: puda
description: Use when introducing PUDA, setting up the PUDA CLI, initializing a project, or updating installed PUDA skills.
---

## PUDA context

PUDA, the Physical Unified Device Architecture, is a hardware-agnostic and LLM-agnostic runtime for Physical AI. It gives AI agents and software systems a unified, verifiable control plane for physical machines by separating high-level agent logic from low-level machine execution.

At a high level, PUDA uses a message-driven architecture built around NATS, a CLI-first interface for agents and humans, declarative protocols for experiment or workflow execution, edge services that translate commands into native machine driver calls, and project records that preserve command/data provenance. Treat PUDA as the agent-native bridge between planning, machine control, execution logs, and generated reports.

Source context: https://www.puda.co/blog/whitepaper

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
