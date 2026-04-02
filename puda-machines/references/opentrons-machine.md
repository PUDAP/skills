---
name: opentrons-machine
description: Generate commands and full protocols for Opentrons OT-2 liquid handling robots, including all command types, labware loading, tip management, pipetting, and protocol code generation.
---

# Opentrons Machine Skills

> Source: [PUDAP/opentrons — driver/protocol.py](https://github.com/PUDAP/opentrons/blob/main/driver/protocol.py)

Generate commands and complete runnable protocols for Opentrons OT-2 liquid handling robots.

## Purpose

This skill enables generation of Opentrons protocol commands that compile into valid OT-2 Python protocol code via `Protocol.to_python_code()`. Commands automate liquid handling operations including aspiration, dispensing, mixing, tip management, deck configuration, looping over CSV data, and flow rate control.

## When to Use

Load this skill when:
- Users describe protocols to be executed on an Opentrons OT-2 robot
- Converting manual lab protocols into automated PUDA protocols for Opentrons
- Processing natural language instructions for Opentrons liquid handling operations
- Working with workflows that involve aspiration, dispensing, mixing, or tip management on an Opentrons deck

## Required Resources

**IMPORTANT**: Before generating any commands, **always consult these resources**:

1. **Consult CLI**: Run `puda machine commands opentrons` to review available commands and parameters
2. **Labware Help**: See [labwares](labware.md) for available labware and details

**Do not generate commands without first consulting these resources** to ensure accuracy and compatibility.

---

## Protocol Structure

Every protocol is a `Protocol` object with the following top-level fields:

| Field | Type | Description |
|---|---|---|
| `protocol_name` | string | Human-readable protocol name |
| `author` | string | Protocol author |
| `description` | string | Short description of the protocol |
| `robot_type` | string | Always `"OT-2"` |
| `api_level` | string | Always `"2.23"` |
| `commands` | list | Ordered list of `ProtocolCommand` objects |

Each `ProtocolCommand` has:
- `command_type` — one of the command names listed below
- `params` — a dict of parameters specific to that command

**Required protocol order:**
1. `load_labware` commands (all labware used in the protocol)
2. `load_instrument` commands (all pipettes)
3. `home` (homes all axes)
4. Pipetting / liquid handling commands
5. Protocol must always end with **no tip attached**

---

## Command Reference

### `load_labware`

Loads a labware onto a deck slot. Must come before any command that references that labware.

| Param | Required | Description |
|---|---|---|
| `name` | yes | Unique reference name used in subsequent commands |
| `labware_type` | yes | Load name from [labware.md](labware.md) |
| `location` | yes | Deck slot (OT-2: `"1"`–`"11"`) — **always ask the user; never assume** |

> **Custom labware** (`mass_balance_vial_30000`, `mass_balance_vial_50000`): automatically loaded via `protocol.load_labware_from_definition()` — the definition is inlined in the generated code. No separate upload required.

**Example:**
```json
{
  "command_type": "load_labware",
  "params": {
    "name": "plate",
    "labware_type": "corning_96_wellplate_360ul_flat",
    "location": "1"
  }
}
```

---

### `load_instrument`

Loads a pipette onto a mount with optional tip racks.

| Param | Required | Description |
|---|---|---|
| `name` | yes | Unique reference name used in subsequent commands |
| `instrument_type` | yes | Pipette type (see pipette table below) |
| `mount` | yes | `"left"` or `"right"` |
| `tip_racks` | no | List of labware `name` values to use as tip racks |

**Example:**
```json
{
  "command_type": "load_instrument",
  "params": {
    "name": "p300",
    "instrument_type": "p300_single_gen2",
    "mount": "right",
    "tip_racks": ["tips"]
  }
}
```

---

### `home`

Homes all robot axes. Must be the **first** movement command after `load_labware` / `load_instrument`.

No params required.

---

### `pick_up_tip`

Picks up a tip. Must occur before any `aspirate` or `dispense`.

| Param | Required | Description |
|---|---|---|
| `pipette` | yes | Pipette `name` from `load_instrument` |
| `labware` | no | Tip rack `name` — if omitted, uses next available tip from tip_racks |
| `well` | no | Well on tip rack (e.g. `"A1"`) — only used if `labware` is specified |

---

### `drop_tip`

Drops the current tip. Every protocol must end with no tip attached.

| Param | Required | Description |
|---|---|---|
| `pipette` | yes | Pipette `name` |
| `labware` | no | Labware to drop tip into (e.g. trash) |
| `well` | no | Well to drop tip into |

---

### `aspirate`

Aspirates liquid from a well.

| Param | Required | Description |
|---|---|---|
| `pipette` | yes | Pipette `name` |
| `volume` | yes | Volume in µL (> 0, ≤ pipette max) |
| `labware` | no | Source labware `name` |
| `well` | no | Source well (e.g. `"A1"`) |
| `aspirate_rate` | no | Flow rate multiplier |
| position ref | no | One of: `aspirate_ref`, `aspirate_position`, `aspirate_height_ref`, `position`, `ref` → `"top"` or `"bottom"` |
| offset | no | One of: `aspirate_offset`, `aspirate_height`, `aspirate_z_offset`, `offset`, `z_offset` → float (mm) |

---

### `dispense`

Dispenses liquid into a well.

| Param | Required | Description |
|---|---|---|
| `pipette` | yes | Pipette `name` |
| `volume` | yes | Volume in µL (> 0, ≤ pipette max) |
| `labware` | no | Destination labware `name` |
| `well` | no | Destination well |
| `dispense_rate` | no | Flow rate multiplier |
| position ref | no | One of: `dispense_ref`, `dispense_position`, `dispense_height_ref`, `position`, `ref` → `"top"` or `"bottom"` |
| offset | no | One of: `dispense_offset`, `dispense_height`, `dispense_z_offset`, `offset`, `z_offset` → float (mm) |

---

### `transfer`

High-level compound command — automatically handles pick_up_tip, aspirate, dispense, drop_tip. Auto-chunks volumes exceeding the pipette maximum.

| Param | Required | Description |
|---|---|---|
| `pipette` | yes | Pipette `name` |
| `volume` | yes | Volume in µL |
| `source_labware` | yes | Source labware `name` |
| `source_well` | yes | Source well |
| `dest_labware` | yes | Destination labware `name` |
| `dest_well` | yes | Destination well |
| `rate` | no | Unified flow rate for aspirate + dispense |
| `aspirate_rate` | no | Aspirate-only flow rate (overrides `rate`) |
| `dispense_rate` | no | Dispense-only flow rate (overrides `rate`) |
| source position ref | no | `source_ref`, `source_position`, `source_height_ref` → `"top"` or `"bottom"` |
| source offset | no | `source_offset`, `source_height`, `source_z_offset` → float (mm) |
| dest position ref | no | `dest_ref`, `dest_position`, `dest_height_ref` → `"top"` or `"bottom"` |
| dest offset | no | `dest_offset`, `dest_height`, `dest_z_offset` → float (mm) |

> **Auto-chunking:** max volume per chunk = 1000 µL for `p1000`, 300 µL for `p300`, 20 µL for all others.

---

### `mix`

Mixes liquid in a well by aspirating and dispensing repeatedly.

| Param | Required | Description |
|---|---|---|
| `pipette` | yes | Pipette `name` |
| `repetitions` | no | Number of mix cycles (default: `3`) |
| `volume` | no | Volume per cycle in µL (default: `100`) |
| `labware` | no | Labware `name` |
| `well` | no | Well |
| position ref | no | `mix_ref`, `mix_position`, `mix_height_ref`, `position`, `ref` → `"top"` or `"bottom"` |
| offset | no | `mix_offset`, `mix_height`, `mix_z_offset`, `offset`, `z_offset` → float (mm) |

---

### `blow_out`

Blows out remaining liquid from the pipette tip.

| Param | Required | Description |
|---|---|---|
| `pipette` | yes | Pipette `name` |
| `labware` | no | Labware `name` |
| `well` | no | Well |
| position ref | no | `blow_ref`, `blow_position`, `blow_height_ref`, `position`, `ref` |
| offset | no | `blow_offset`, `blow_height`, `blow_z_offset`, `offset`, `z_offset` |

---

### `air_gap`

Draws an air gap into the tip after aspirating.

| Param | Required | Description |
|---|---|---|
| `pipette` | yes | Pipette `name` |
| `volume` | no | Air gap volume in µL (default: `10`) |
| `height` | no | Height above well in mm (default: `5`) |

---

### `touch_tip`

Touches the tip to the sides of a well to remove droplets.

| Param | Required | Description |
|---|---|---|
| `pipette` | yes | Pipette `name` |
| `labware` | yes | Labware `name` |
| `well` | yes | Well |
| `radius` | no | Fraction of well radius to touch (default: `1.0`) |
| `v_offset` | no | Vertical offset from top of well in mm (default: `-1`) |
| `speed` | no | Touch speed in mm/s (default: `60`) |

---

### `move_to`

Moves the pipette to a specific position above a well.

| Param | Required | Description |
|---|---|---|
| `pipette` | yes | Pipette `name` |
| `labware` | yes | Labware `name` |
| `well` | yes | Well |
| position ref | no | `move_ref`, `move_position`, `move_height_ref`, `position`, `ref` → `"top"` or `"bottom"` (default: `"top"`) |
| offset | no | `move_offset`, `move_height`, `move_z_offset`, `offset`, `z_offset` → float mm (default: `10` when ref is `"top"`) |

---

### `flow_rate`

Sets the pipette flow rates for aspirate, dispense, and/or blow-out in µL/s.

| Param | Required | Description |
|---|---|---|
| `pipette` | yes | Pipette `name` |
| `aspirate` | no | Aspirate flow rate in µL/s |
| `dispense` | no | Dispense flow rate in µL/s |
| `blow_out` | no | Blow-out flow rate in µL/s |

---

### `delay`

Pauses the protocol for a specified duration.

| Param | Required | Description |
|---|---|---|
| `seconds` | no | Delay in seconds |
| `minutes` | no | Delay in minutes |
| `message` / `text` / `comment` | no | Message to display during delay |
| `pipette` | no | If set, uses `pipette.delay()` instead of `protocol.delay()` |

---

### `comment`

Inserts a comment line into the generated protocol code.

| Param | Required | Description |
|---|---|---|
| `text` | yes | Comment text |

---

### `read_csv_file` / `read_csv`

Reads a CSV file into a `data` list for use in a `loop`. Does not generate protocol code itself.

| Param | Required | Description |
|---|---|---|
| `file_path` | yes | Path to the CSV file on the robot |
| `csv_data` | no | Inline CSV data as a list of dicts (bypasses file read) |

---

### `loop` / `loop_over_csv`

Iterates over rows in `data` (populated by `read_csv`). Each iteration exposes the current row as `row['column_name']`.

| Param | Required | Description |
|---|---|---|
| `commands` | yes | List of sub-commands to execute per row |

> Inside loop sub-commands, use `row['column_name']` as any param value to reference CSV columns dynamically.

---

## Pipette Types

| Pipette type | Volume range | Channels |
|---|---|---|
| `p10_single_gen2` | up to 10 µL | single |
| `p10_multi_gen2` | up to 10 µL | 8 |
| `p20_single_gen2` | up to 20 µL | single |
| `p20_multi_gen2` | up to 20 µL | 8 |
| `p300_single_gen2` | up to 300 µL | single |
| `p300_multi_gen2` | up to 300 µL | 8 |
| `p1000_single_gen2` | up to 1000 µL | single |
| `p1000_multi_gen2` | up to 1000 µL | 8 |

---

## Rules and Restrictions

### Handling Missing Information

- If any information is missing from the user's request, **do not assume or guess values**. Use a placeholder (e.g., `"PLACEHOLDER"`) and explicitly ask the user.
- If the labware only has one well, it is safe to assume `well: "A1"` without asking.
- **`location` (deck slot) for `load_labware`**: **Always ask the user** which deck slot each labware should be placed on. Do **not** assume or assign default slot numbers. Wait for the user to confirm the slot before generating the command.

### Available Deck Slots

- **OT-2 valid deck slots**: `"1"` – `"11"` (string)
- Confirm with the user if the slot is ambiguous.

### Critical Sequencing Rules

1. **`load_labware`** and **`load_instrument`**: Must come before all other commands.
2. **`home`**: Must be the first movement command, placed after all load commands.
3. **`pick_up_tip`**: Must be called before any `aspirate` or `dispense`. Only one tip at a time.
4. **`drop_tip`**: Must follow every `pick_up_tip`. Protocol must always end with no tip attached.
5. **`aspirate`** / **`dispense`**: May only occur after a tip has been picked up.
6. **`read_csv_file`** / **`read_csv`**: Must appear before the `loop` that uses its data.

### Volume Constraints

- `aspirate` / `dispense` volume must be > 0 and ≤ pipette maximum volume.
- `transfer` auto-chunks volumes exceeding the pipette max — no manual chunking needed.

### Custom Labware

- `mass_balance_vial_30000` and `mass_balance_vial_50000` are custom labware.
- These are automatically loaded via `protocol.load_labware_from_definition()` — the definition is embedded inline in the generated protocol code. No separate upload step is needed.

---

## Instructions

1. **Consult Resources**: Run `puda machine commands opentrons` and review [labware.md](labware.md) before generating any commands.

2. **Verify sequencing and constraints**: Always verify commands follow all rules above — correct load order, `home` placement, `pick_up_tip` → pipetting → `drop_tip` sequencing, valid deck slots, labware compatibility, and volume constraints.

3. **Generate the protocol**: Build a `Protocol` object with `machine_id: "opentrons"`, populate the `commands` list using the command types above, and ensure the protocol generates valid runnable OT-2 Python code via `Protocol.to_python_code()`.
