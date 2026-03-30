---

## name: dobot-m1pro-machine
description: Generate commands for Dobot M1Pro gripper workflows that transfer tubes between fixed hardcoded positions.

# Dobot M1Pro Machine Skills

Generate commands for Dobot M1Pro gripper-based tube transfer workflows.

## Purpose

This reference helps generate commands for Dobot M1Pro operations that use a gripper to pick up and move tubes between known positions in the workspace.

## When to Use

Load this reference when:

- Users ask to transfer tubes with a gripper
- A workflow needs pick-and-place tube movement between fixed positions
- The user refers to hardcoded Dobot M1Pro positions

## Required Resources

Before generating commands, consult the puda CLI:

- **Machine Help**: Use `puda machine commands dobot-m1pro` to see available commands, parameters, and options

Do not invent command names or parameters. If the CLI output does not expose a requested operation, explain that gap to the user instead of guessing.

## Command Structure

Each Dobot M1Pro machine command follows the standard protocol command structure (see protocol-generator reference). Key Dobot M1Pro details:

- `machine_id`: Must be `"dobot-m1pro"` (string)
- `name`: Must be a valid Dobot M1Pro command returned by `puda machine commands dobot-m1pro`
- `params`: Use only parameters supported by the CLI for that command

## Arm Methods

- `**arm.pick_from(position=[...])`** — Use to pick up a tube from a centrifuge-tube MTP position.
- `**arm.place_to(position=[...])**` — Use to place a tube into a destination position (e.g. Centrifuge-2 slot).

## Centrifuge-2 Positions

Centrifuge-2 is a 6-slot circular holder. Slots are evenly spaced at 60° intervals. Use `arm.place_to(position=[...])` to place tubes into these slots.

The `r` value rotates the gripper so it stays parallel to each slot (rotates 60° per slot, with 180° symmetry).


| Slot | Coordinates            |
| ---- | ---------------------- |
| 1    | `[214, -77, 82, 20]`   |
| 2    | `[228, -54, 82, -40]`  |
| 3    | `[254, -54, 82, -100]` |
| 4    | `[268, -77, 82, 20]`   |
| 5    | `[254, -100, 82, 140]` |
| 6    | `[228, -100, 82, 80]`  |

## Centrifuge-1 Positions

Centrifuge-1 is identical in layout to Centrifuge-2 but offset **+150 mm in y**. Gripper angles are the same.

| Slot | Coordinates           |
| ---- | --------------------- |
| 1    | `[214, 73, 82, 20]`   |
| 2    | `[228, 96, 82, -40]`  |
| 3    | `[254, 96, 82, -100]` |
| 4    | `[268, 73, 82, 20]`   |
| 5    | `[254, 50, 82, 140]`  |
| 6    | `[228, 50, 82, 80]`   |

## Centrifuge-Tube MTP Positions

The MTP is a 4-row (A–D) × 6-column (1–6) grid. Positions are `[x, y, z, r]` coordinates.

**Grid rule:**

- Each column step (1 → 2 → … → 6) subtracts **20** from the first value (x), starting at x = 283.
- Each row step (A → B → C → D) subtracts **20** from the second value (y), starting at y = −177.
- The third and fourth values are always `60` and `−70`.

### Row A (y = −177)

| Position | Coordinates            |
| -------- | ---------------------- |
| A1       | `[283, -177, 60, -70]` |
| A2       | `[263, -177, 60, -70]` |
| A3       | `[243, -177, 60, -70]` |
| A4       | `[223, -177, 60, -70]` |
| A5       | `[203, -177, 60, -70]` |
| A6       | `[183, -177, 60, -70]` |

### Row B (y = −197)

| Position | Coordinates            |
| -------- | ---------------------- |
| B1       | `[283, -197, 60, -70]` |
| B2       | `[263, -197, 60, -70]` |
| B3       | `[243, -197, 60, -70]` |
| B4       | `[223, -197, 60, -70]` |
| B5       | `[203, -197, 60, -70]` |
| B6       | `[183, -197, 60, -70]` |

### Row C (y = −217)

| Position | Coordinates            |
| -------- | ---------------------- |
| C1       | `[283, -217, 60, -70]` |
| C2       | `[263, -217, 60, -70]` |
| C3       | `[243, -217, 60, -70]` |
| C4       | `[223, -217, 60, -70]` |
| C5       | `[203, -217, 60, -70]` |
| C6       | `[183, -217, 60, -70]` |

### Row D (y = −237)

| Position | Coordinates            |
| -------- | ---------------------- |
| D1       | `[283, -237, 60, -70]` |
| D2       | `[263, -237, 60, -70]` |
| D3       | `[243, -237, 60, -70]` |
| D4       | `[223, -237, 60, -70]` |
| D5       | `[203, -237, 60, -70]` |
| D6       | `[183, -237, 60, -70]` |


If the user requests a position that is not listed here, do not guess. Ask for the exact position or confirm whether one of the hardcoded positions should be used.

## Required Information

Before generating a Dobot M1Pro command, confirm:

- Which tube should be moved
- The source position (use `arm.pick_from` for MTP pickup)
- The destination position (use `arm.place_to` for centrifuge placement or other targets)

If required information is missing, do not assume it. Ask the user, or use an explicit placeholder only when the surrounding workflow requires drafting an incomplete command for review.

## Rules and Restrictions

Apply these rules when preparing Dobot M1Pro commands:

- Use only the hardcoded positions listed in this document unless the user provides another exact position
- Use `arm.pick_from(position=...)` when picking tubes from centrifuge-tube MTP positions
- Use `arm.place_to(position=...)` when placing tubes into Centrifuge-2 slots or any other destination
- Treat tube transfers as gripper-based pick-and-place operations
- Ask for missing source or destination details instead of guessing

## Instructions

1. **Consult CLI**: Run `puda machine commands dobot-m1pro` to review available commands and parameters.
2. **Match the operation**: Choose the Dobot M1Pro command that best matches the requested tube transfer.
3. **Resolve positions**: Use the MTP grid and Centrifuge-2 slot positions from this document when applicable.
4. **Pick from MTP**: Use `arm.pick_from(position=[...])` to pick a tube from an MTP slot.
5. **Place into centrifuge**: Use `arm.place_to(position=[...])` to place a tube into a Centrifuge-2 slot.
6. **Generate command**: Create a command object with `machine_id: "dobot-m1pro"`, a valid `name`, and supported `params`.

## Best Practices

- Prefer named positions (e.g. MTP A1, Centrifuge-2 Slot 3) over repeating raw coordinates in explanations.
- Keep source and destination positions explicit in every transfer step.
- Use `arm.pick_from` for MTP pickups and `arm.place_to` for centrifuge placements and all other destinations.
- Ask for missing transfer details instead of guessing.

