---
name: puda
description: Use when introducing PUDA, setting up the PUDA CLI, initializing a project, updating installed PUDA skills, syncing host clocks to an NTP server with Chrony, or publishing USB/IP camera livestreams over RTSP, RTMP, HLS, or WebRTC.
---

## PUDA context

PUDA, the Physical Unified Device Architecture, is a hardware-agnostic and LLM-agnostic runtime for Physical AI. It gives AI agents and software systems a unified, verifiable control plane for physical machines by separating high-level agent logic from low-level machine execution.

At a high level, PUDA uses a message-driven architecture built around NATS, a CLI-first interface for agents and humans, declarative protocols for experiment or workflow execution, edge services that translate commands into native machine driver calls, and project records that preserve command/data provenance. Treat PUDA as the agent-native bridge between planning, machine control, execution logs, and generated reports.

For more information on PUDA, setup, or any other questions, refer to https://docs.puda.co/llms.txt.

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

## Clock sync (Chrony / NTP)

PUDA timestamps, discovery leases, and experiment provenance depend on host clocks. When setting up a site or edge host, or when clocks, Chrony, or NTP come up, read [references/chrony.md](references/chrony.md). Sync the **host** to the site NTP server. If you are unsure of the NTP server host IP, ask the user — do not assume. Do not run Chrony inside an edge container.

## Livestream (USB / IP cameras)

When a machine host has a USB camera, webcam, or IP camera and operators need live video, read [references/livestream.md](references/livestream.md). Use [PUDAP/livestream](https://github.com/PUDAP/livestream).

**Ask the user** for the camera (USB `/dev/video*` path or network `rtsp://` URL) and the livestream name. Do not assume either. Then configure `streams.conf` / `compose.yml` and start the Docker stack with those values. List `/dev/video*` on the host before asking which USB camera to use.

## Updating puda skills

To refresh or update puda skills:

```bash
puda skills update
```
