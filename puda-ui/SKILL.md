---
name: puda-ui
description: Create Streamlit manual-control frontends backed by the PUDA CLI. Use when building operator UIs, manual machine control panels, or apps that start/complete/reset PUDA runs from buttons.
---

# PUDA UI (manual control)

Build Streamlit operator UIs that drive machines through the **PUDA CLI**. The CLI remains the control plane; the UI only shells out to `puda`.

For Streamlit layout, widgets, and styling, also follow the `developing-with-streamlit` skill.

## Required session controls

Every manual-control UI **must** include these three buttons:

| Button | Role |
|--------|------|
| **Start** | Open a manual run on all relevant machines |
| **Complete** | Close the manual run on all relevant machines |
| **Reset** | Reset a machine via CLI |

### UI state machine

1. **Idle (default):** Only **Start** is enabled. All other controls (machine actions, **Complete**, **Reset**, params) are greyed out / disabled.
2. **Start pressed:** Send a **start** immediate command via the PUDA CLI with `run_id` of `"manual"` to **every relevant machine**. On success, unlock the other buttons and machine controls.
3. **Complete pressed:** Send a **complete** command via the PUDA CLI (same `run_id` `"manual"`) to the relevant machines. On success, return to idle (everything greyed out again except **Start**).
4. **Reset pressed:** Run `puda machine reset <machine_id>` for the target machine. Prefer returning to idle after a successful reset of the session machines.

Do not send machine action commands until **Start** has succeeded for the current session.

## CLI backend

Always invoke `puda` from the project root (where `puda.config` / `project.md` live). Capture stdout/stderr and show failures in the UI.

If `puda machine start` or `puda machine complete` is missing / unknown, tell the user to update the PUDA CLI to version **>= 0.0.35** (e.g. `puda version`, then `puda update`).

### Start

Send start immediate to all relevant machines with fixed run id `manual`:

```bash
puda machine start <machine_ids> --run-id manual
```

`<machine_ids>` may be comma-separated (same pattern as `puda machine reset biologic,first`).

### Complete

```bash
puda machine complete <machine_ids> --run-id manual
```

Use the **same** machine set and `run_id` (`manual`) that Start used.

### Reset

```bash
puda machine reset <machine_id>
```

Reset targets one machine id (or comma-separated ids if the operator is resetting several).

### Relevant machines

Resolve the machine set from the app’s configured targets (project memory, user selection, or workflow skill). Start and Complete must hit the **same** set for a session. Discover with `puda machine list` when needed; confirm ambiguous targets with the user.

## Implementation rules

- Backend = subprocess/`puda` only. Do not open a parallel NATS client from the UI.
- Keep `run_id` hard-coded to `"manual"` for Start and Complete in manual-control UIs.
- Gate every non-Start control on session state (`started == True`).
- Surface CLI errors; do not flip UI state to “started” or “idle” if the corresponding Start/Complete call failed.
- Prefer a small helper module (e.g. `puda_cli.py`) that wraps start / complete / reset / list so buttons stay thin.

## Scaffold checklist

When creating a new manual-control app:

- [ ] Streamlit entrypoint (e.g. `app.py` / `streamlit_app.py`)
- [ ] Session state: idle vs started; list of relevant `machine_id`s
- [ ] **Start**, **Complete**, **Reset** always present
- [ ] Idle: disable everything except **Start**
- [ ] Start → `puda machine start … --run-id manual`
- [ ] Complete → `puda machine complete … --run-id manual`
- [ ] Reset → `puda machine reset <machine_id>`
- [ ] Machine action buttons only enabled after Start
