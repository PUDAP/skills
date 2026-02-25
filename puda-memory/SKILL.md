---
name: puda-memory
description: Maintains experiment.md as the single source of truth for an experiment. Use after creating or updating protocols, or after running protocols, to record logs, protocol links, and history with timestamps.
---

# Puda Memory

## Goal

Maintain **experiment.md** as the source of truth for each experiment: logs, protocol links, and a chronological history so runs are reproducible and auditable.

**CRITICAL**: Persist all experiment-related state so runs are reproducible and auditable.

Each experiment folder has **experiment.md** as the single place to record everything about that experiment for long-term memory. Paths below are relative to the experiment folder (which contains `protocols/` and `logs/`).

## When to Update

- After **creating** a protocol file
- After **updating** or deriving a new protocol
- After **every** protocol run and log file is generated (append the run entry and the new log path)

## What to Record in experiment.md

- **Logs**: Use explicit markdown links to log files under `logs/`, e.g. `[<run_id>](logs/<run_id>.log)`. Add a new log link each time a protocol is run.
- **Protocols**: Use explicit markdown links to protocol files under `protocols/`. In the "Protocols" section, list each as `[<protocol_id>](protocols/<protocol_id>.json)` with an optional short description after the link (e.g. `[<protocol_id>](protocols/<protocol_id>.json) — changed dispense amount to 100ul in step 10`).
- **History**: A chronological log of actions with ISO 8601 timestamps. **MUST** use a real timestamp—never guess or use a placeholder. Get the timestamp from the relevant file: for "ran" entries use the first line of the log file; for "created"/"updated" entries use the `timestamp` key in the protocol JSON file. Use explicit markdown links for all file paths. Append one line per action in this form:
  - `<timestamp> created [<protocol_id>](protocols/<protocol_id>.json)`
  - `<timestamp> updated [<old_protocol_id>](protocols/<old_protocol_id>.json) to [<new_protocol_id>](protocols/<new_protocol_id>.json)`
  - `<timestamp> ran [<protocol_id>](protocols/<protocol_id>.json) — logs: [<log_id>](logs/<log_id>.log)`
