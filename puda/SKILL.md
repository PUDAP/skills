---
name: puda
description: Use when introducing PUDA, setting up or upgrading the CLI, managing profiles and user config, discovering machines and watching telemetry, initializing projects, updating skills, syncing host clocks with Chrony, or publishing USB/IP camera livestreams.
---

## PUDA context

PUDA, the Physical Unified Device Architecture, is a hardware-agnostic and LLM-agnostic runtime for Physical AI. It gives AI agents and software systems a unified, verifiable control plane for physical machines by separating high-level agent logic from low-level machine execution.

At a high level, PUDA uses a message-driven architecture built around NATS, a CLI-first interface for agents and humans, declarative protocols for experiment or workflow execution, edge services that translate commands into native machine driver calls, and project records that preserve command/data provenance. Treat PUDA as the agent-native bridge between planning, machine control, execution logs, and generated reports.

For more information on PUDA, setup, or any other questions, refer to https://docs.puda.co/llms.txt.

## Setup puda

1. **Install CLI**: Ensure `puda` is installed and on your PATH so it can be invoked globally. If missing, download the binary for your platform from the [Puda releases page](https://github.com/PUDAP/puda/releases), install it, and add it to PATH.
2. **Ensure dependencies**: Ensure `python3`, `pip`, and `npx` are available; install them first if missing.
3. **Login**: Ask the user for their username if not already known — do not assume. Log in with `puda login -u <username>`.
4. **Select a NATS profile**: Inspect `puda profile list` and `puda profile current`. Use an existing intended profile with `puda profile switch <name>`. For a new profile, get the name and broker URLs from the user or deployment configuration; do not assume the lab. Plaintext: `puda profile add <name> --servers <nats-urls>`. Encrypted: `puda profile add <name> --servers <tls-urls> --ca <local-ca-path> --key <local-key-path>`. Both files are required for an encrypted CLI profile. The first profile is activated automatically if none is selected; otherwise explicitly switch to the intended profile. Read [CLI profiles and telemetry](references/cli-profiles-and-telemetry.md) when configuring or migrating connections.
5. **Install skills**: Run `puda skills install` to install agent skills for puda.

## Setup project

Run `puda init` (e.g. `puda init .` or `puda init <folder_name>`).

Only after puda is set up and the project is initialized, proceed with protocol generation, machine commands, or experiment workflows.

## CLI 0.1.x configuration and machine inspection

Use `puda --version` and command `--help` to check the installed interface. This skill targets CLI 0.1.3; the Python SDK has a separate version (0.0.21).

- `puda config list/get/set` manages only `user.user_id` and `user.username`. Broker URLs and security paths belong to `puda profile`; project settings belong to `puda project config`. Do not use the removed `puda config set nats_servers` workflow.
- `puda machine list` discovers responsive machines. `puda machine info <id>` (alias `ping`) returns live status, SDK version, registered livestreams, and advertised telemetry streams. Read `results[].tlm_streams[].subject`; do not guess a stream exists from the machine name.
- `puda machine watch <full-subject> --timeout 15` observes live traffic. Use an advertised subject such as `puda.first.tlm.stream.pos`. Positional arguments are subjects, not machine IDs. To watch all topics for specific machines, use `--machines first,balance` instead of subjects.
- Profile and machine inspection output is JSON by default; watch emits NDJSON. Use `--human` only when text is wanted. Prefer bounded watches for inspection; use continuous watches when requested. These read-only commands do not require initializing a project or starting a machine run.

For profile migration, editable config fields, machine info output, watch wildcards, heartbeat filtering, and subject examples, read [CLI profiles and telemetry](references/cli-profiles-and-telemetry.md).

## Project Folder Structure

```text
.
├── project.md                        # single source of truth (puda-memory skill)
├── protocols/                        # generated protocol files (puda-protocol skill)
├── puda.config                       # puda config file
└── puda.db                           # puda database file
```

## Clock sync (Chrony / NTP)

PUDA timestamps, discovery leases, and experiment provenance depend on host clocks. When setting up a site or edge host, or when clocks, Chrony, or NTP come up, read [references/chrony.md](references/chrony.md). On an **edge** host, ask the user for the site NTP server IP and run [`scripts/sync-clock.sh`](scripts/sync-clock.sh) or [`scripts/sync-clock.ps1`](scripts/sync-clock.ps1). Do not assume the IP. Do not run Chrony inside an edge container.

## Livestream (USB / IP cameras)

When a machine host has a USB camera, webcam, or IP camera and operators need live video, read [references/livestream.md](references/livestream.md). Use [PUDAP/livestream](https://github.com/PUDAP/livestream).

**Ask the user** for the camera (USB `/dev/video*` path or network `rtsp://` URL), the livestream name, a short description, the MediaMTX **host** (MagicDNS, Tailscale IP, or the machine IP if there is no Tailscale), and the **machine IDs** that should use this feed (one or many). Do not assume any of these. Then start the Docker stack and register with `puda livestream add --name --host --description --machines`. Livestreams are fleet records, not edge config.

## Updating puda skills

To refresh or update puda skills:

```bash
puda skills update
```
