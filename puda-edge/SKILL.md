---
name: puda-edge
description: >-
  Write, configure, and remotely update PUDA Python edge services. Use when
  creating or editing driver.py or main.py, adding @command or @safety,
  scaffolding from the SDK/API or GUI edge templates, integrating a new machine,
  building GUI-controlled instruments from manuals or screenshots and task
  instructions, or running puda machine update.
---

# Puda Edge

Help write Python edge services: thin hardware wrappers that connect to NATS and advertise machine commands.

## Build an edge

Use an existing machine SDK/API when suitable. For instruments operated through desktop software, build a GUI edge: the AI uses a manual or screenshots with task instructions to write machine-specific Python workflows, which PUDA exposes over NATS.

For GUI work, read [references/gui-edge.md](references/gui-edge.md). Clone [PUDAP/edge-python-gui-template](https://github.com/PUDAP/edge-python-gui-template) from GitHub as the scaffold and use [PUDAP/opentrons-gui-edge](https://github.com/PUDAP/opentrons-gui-edge) as the worked example. The guide covers translating task instructions into deterministic GUI commands and validating them. Use a vendor PDF manual when available. Without a manual, screenshots showing where to click, what to type, and the expected result are valid context for an atomic command. Supplement either source with live captures when available.

For SDK/API and GUI edges:

- Inspect the selected template's dependencies and SDK contract before scaffolding. The GUI examples use `from puda import EdgeNatsClient, EdgeRunner, command`.
- Keep machine commands typed, JSON-compatible, and documented with parameters, units, defaults, prerequisites, returned evidence, and failures. Expose intended workflows with `@command`. For GUI edges, `capture_screenshot` is the only low-level remote command; use inherited GUI helpers internally to implement high-level workflows.
- Configure machine identity, NATS servers, and connection/window details through settings and `.env.example`. Preserve the template's lifecycle and cleanup. Do not copy credentials or a working `.env` from another machine.
- Verify commands offline before desktop or hardware validation. Report separately what was implemented, tested with fixtures, observed on the desktop, and exercised on hardware.

Follow [Integrating a New Machine](https://docs.puda.co/docs/0.1.0/setup/integrating-a-new-machine) for repo layout, `main.py` config, telemetry, and multi-machine PCs. For SDK/API edges, scaffold from [edge-python-template](https://github.com/PUDAP/edge-python-template); for GUI edges, use the GUI template above. Name the repo `puda-<machine_id>-edge`.

Python only. For host/NATS/hardware commissioning, use **puda-deployment**. After commands work, install the CLI with **puda**.

## Scaffold

1. Create the repo from the template. Resolve every `TODO`.
2. Set a unique lowercase hyphenated `MACHINE_ID` in `.env` with `NATS_SERVERS`.
3. Implement `driver.py`, then wire config and the driver into `main.py`.
4. Keep helpers private (`_name`). Only `@command` methods are advertised.

Verify with `puda machine commands <machine_id>` after the edge is connected.

Several instruments on one PC can share one uv workspace; each subdirectory gets its own `MACHINE_ID`, `driver.py`, and `main.py`. See the docs and [PUDAP/ViPSA](https://github.com/PUDAP/ViPSA).

## Driver

`driver.py` is a thin wrapper around the hardware API. Method names, docstrings, parameters, and return annotations are the command interface agents see. Put a one-sentence summary on the **Driver class docstring**; `EdgeRunner` advertises the first paragraph on `puda machine list` and `puda machine ping` so agents do not need `puda machine commands` just to learn what the machine is.

- Decorate every remotely callable method with `@command`. Undecorated public methods are not advertised or callable over NATS. A driver with no `@command` methods fails at startup.
- Keep commands atomic: one hardware action per method.
- Parameters must be primitives (`str`, `int`, `float`, `bool`) or simple lists/dicts of primitives.
- Document args, returns, and raised errors in every public docstring; they provide context for agents.
- Raise on failure with the command, targets, and hardware response. Returning `False` is still a successful PUDA response (`{"result": false}`).
- `shutdown`, `home`, and `reset` are optional. `shutdown` runs before the edge stops. `home` is triggered by `puda machine home`. `puda machine reset` always clears the active `run_id`, then calls `reset` if present.

```python
from puda import command, safety

class Driver:
    """Software-only PUDA test machine. Commands are simulated in memory; no hardware is required."""

    @command
    def shutdown(self) -> bool:
        """Release hardware resources. If defined, called before the edge stops."""
        ...

    @command
    def home(self) -> bool:
        """Home the machine. If defined, triggered by `puda machine home <machine_id>`."""
        ...

    @command
    def reset(self) -> bool:
        """Software reset. Optional. `puda machine reset` clears the run first, then calls this if present."""
        ...

    @command
    def move_to(self, x_mm: float, y_mm: float, z_mm: float) -> bool:
        """
        Move the machine head to an absolute position.

        Args:
            x_mm: Target X position in millimeters.
            y_mm: Target Y position in millimeters.
            z_mm: Target Z position in millimeters.

        Raises:
            RuntimeError: If the hardware rejects the move.
        """
        result = self._hardware.move_to(x_mm=x_mm, y_mm=y_mm, z_mm=z_mm)
        if not result.ok:
            raise RuntimeError(
                "Failed to move machine head "
                f"to x={x_mm}, y={y_mm}, z={z_mm}: {result.error}"
            )
        return True
```

## `@safety`

Attach `@safety` to a `@command` method to publish advisory context in the command catalog. It does not block edge dispatch. `@safety` without `@command` is ignored.

All five fields are keyword-only. Do not add others.

| Field | Required | Role |
|---|---|---|
| `summary` | yes | Headline of the risk |
| `hazards` | no | Short tags such as `collision`, `thermal` |
| `requires` | no | Preconditions; agents insert earlier steps or ask first |
| `forbidden_when` | no | Situations where the command must not be used |
| `confirm` | no | Operator `yes` gate. Defaults to `false`. Set `true` to opt in |

Do not repeat the same sentence across fields. `summary` names the risk; `requires` is the precondition; `forbidden_when` is the veto; `confirm=True` is the prompt. Do not put "confirm…" in `summary`.

```python
@command
@safety(
    summary="Collision risk from unhomed motion or an occupied workspace.",
    hazards=["collision"],
    requires="Machine must just have been homed.",
    forbidden_when="Do not move if the workspace is occupied or human movement is detected.",
    confirm=True,
)
def move_to(self, x: float, y: float, z: float) -> dict:
    ...
```

Omit `@safety` on read-only or harmless commands (`get_position`, `echo`). Use `confirm=True` for motion, chemical mixing, heat, pressure, or other irreversible hardware actions.

## Configure

Keep `MACHINE_ID` and `NATS_SERVERS` in `.env`. Add typed hardware fields to `Config` in `main.py` so missing values fail at startup. Pass those fields into `Driver(...)`.

Telemetry must be JSON-serializable. Publish heartbeat plus whatever position, health, and state the machine actually has. Field names should match the hardware (joints, plunger, focus), not a cartesian template.

## Remote updates

```bash
puda machine update
```

Check `puda machine update --help` for the installed CLI's targeting and update options before using it.
