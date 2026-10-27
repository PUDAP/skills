---
name: puda
description: Set up the PUDA CLI and projects, configure connection profiles, inspect machines and telemetry, synchronize host clocks, and publish camera livestreams. Use for PUDA setup and fleet inspection.
---

# PUDA

PUDA (Physical Unified Device Architecture) connects agents to physical machines through a CLI, NATS messaging, declarative protocols, and Python edge services. Project records preserve command and data provenance.

Check `puda --version` and command `--help` before using the installed interface. These references target CLI 0.1.3; the Python SDK is versioned separately (0.0.21). For additional documentation, use https://docs.puda.co/llms.txt.

## Read only what the task needs

- **Install, upgrade, log in, initialize a project, or update skills:** read [setup](references/setup.md).
- **Configure connections, inspect machines, or watch telemetry:** read [CLI profiles and telemetry](references/cli-profiles-and-telemetry.md).
- **Configure host clocks:** read [Chrony / NTP](references/chrony.md); use the bundled [Linux](scripts/sync-clock.sh) or [Windows](scripts/sync-clock.ps1) helper when appropriate.
- **Publish a USB/IP camera:** read [livestream setup](references/livestream.md).

## Essential constraints

- Inspect the active profile; obtain the intended lab, broker, and credentials from the user or deployment configuration rather than assuming them.
- User identity belongs to `puda config`; broker settings belong to `puda profile`; project settings belong to `puda project config`.
- Discover machines with `puda machine list` and advertised streams with `puda machine info <id>`. `puda machine watch` takes full subjects, or `--machines`; prefer a bounded `--timeout` for inspection.
- Read-only profile/machine inspection needs no initialized project or machine run. Set up PUDA and initialize the project before protocol generation, machine commands, or experiments.
- Obtain the site NTP IP before clock configuration; run Chrony on the host, not inside the edge container. Obtain camera, feed name, description, MediaMTX host, and target machine IDs before publishing video.
