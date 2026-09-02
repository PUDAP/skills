---
name: puda-edge
description: >-
  Write, configure, and remotely update PUDA Python edge services. Use when
  creating or editing driver.py or main.py, adding @command or @safety,
  scaffolding from edge-python-template, integrating a new machine, or running
  puda machine update.
---

# Puda Edge

Help write Python edge services: thin hardware wrappers that connect to NATS and advertise machine commands.

Follow [Integrating a New Machine](https://docs.puda.co/docs/setup/integrating-a-new-machine) for repo layout, `main.py` config, telemetry, and multi-machine PCs. Scaffold from [edge-python-template](https://github.com/PUDAP/edge-python-template). Name the repo `puda-<machine_id>-edge`.

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
- Document args, returns, and raised errors in every public docstring.
- Raise on failure with the command, targets, and hardware response. Returning `False` is still a successful PUDA response (`{"result": false}`).
- Define `shutdown`, `home`, and `reset`.

```python
from puda import command, safety

class Driver:
    """Software-only PUDA test machine. Commands are simulated in memory; no hardware is required."""

    @command
    def shutdown(self) -> bool:
        """Release hardware resources. Used on edge restart."""
        ...

    @command
    def home(self) -> bool:
        """Home the machine. Used by `puda machine home <machine_id>`."""
        ...

    @command
    def reset(self) -> bool:
        """Software reset. Used by `puda machine reset <machine_id>`."""
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

Omit `@safety` on read-only or harmless commands (`get_position`, `echo`). Use `confirm=True` for motion, heat, pressure, or other irreversible hardware actions.

## Configure

Keep `MACHINE_ID` and `NATS_SERVERS` in `.env`. Add typed hardware fields to `Config` in `main.py` so missing values fail at startup. Pass those fields into `Driver(...)`.

Telemetry must be JSON-serializable. Publish heartbeat plus whatever position, health, and state the machine actually has. Field names should match the hardware (joints, plunger, focus), not a cartesian template.

## Remote updates

```bash
puda machine update
```
