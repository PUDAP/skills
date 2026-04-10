---
name: opentrons-machine
description: Generate commands and full protocols for Opentrons OT-2 liquid handling robots, including labware loading, tip management, pipetting, protocol code generation, and camera image capture.
---

# Opentrons Machine Skills

Generate commands and complete runnable protocols for Opentrons OT-2 liquid handling robots.

## Purpose

This skill enables generation of commands for Opentrons OT-2 liquid handling robots. These commands compile into valid OT-2 Python protocol code via `Protocol.to_python_code()`. They automate liquid handling operations including aspiration, dispensing, mixing, tip management, deck configuration, and looping over CSV data.

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

## Command Structure

Each Opentrons command follows the standard protocol command structure (see protocol-generator reference). Key Opentrons-specific details:

- `machine_id`: Must be `"opentrons"` (string)

## Rules and Restrictions

The following rules **must** be strictly followed when generating Opentrons commands:

### Handling Missing Information

- If any information is missing from the user's request, **do not assume or guess values**. Use a placeholder value (e.g., `"PLACEHOLDER"` or `"?"`) in the command and explicitly ask the user to provide the missing information.
- If the labware only has one well, it is safe to assume `well: "A1"` without asking the user.
- **`location` (deck slot) for `load_labware`**: Always ask the user which deck slot each labware should go on. Do **not** assume or assign default slot numbers.

### Available Deck Slots

- **Valid deck slots**: `"1"` – `"11"` (string)
- Confirm with the user if the slot is ambiguous.

### Command Restrictions

- **`aspirate` / `dispense` volume**: Must be > 0 and ≤ the pipette's maximum volume.
- **`transfer`** auto-chunks volumes exceeding the pipette max — no manual chunking needed. Max per chunk: 1000 µL for `p1000`, 300 µL for `p300`, 20 µL for all others.
- **`height_from_bottom` / z offset**: Must be non-negative (≥ 0).

### Pipette Types

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

### Camera Capture

The opentrons edge service supports an attached USB camera via the `capture_image` command. Camera support is **optional** — the command is only available when `CAMERA_DEVICE` is set in the edge `.env`.

**Edge `.env` variables:**
- `CAMERA_DEVICE`: Device index (e.g. `0`) or path (e.g. `/dev/video0`). Overrides `camera_index` at connect time. Leave unset to run without a camera.
- `CAMERA_RESOLUTION`: Resolution as `WIDTHxHEIGHT` (e.g. `1280x720`). Omit to use camera default.
- `CAMERA_CAPTURES_FOLDER`: Folder for saved images. Defaults to `captures` (relative to edge CWD).

**Command:**
```json
{
  "step_number": 1,
  "name": "capture_image",
  "machine_id": "opentrons",
  "params": {
    "filename": "well_A1_capture.jpg"
  }
}
```

**Parameters:**
- `filename` (string, optional): Filename for the saved image. Auto-generates `capture_YYYYMMDD_HHMMSS.jpg` if omitted. `.jpg` appended if no extension given. Relative paths resolve inside `captures_folder`.

**Response:**
- `path` (string): Path of the saved image — `captures_folder/filename`, relative to edge CWD unless `CAMERA_CAPTURES_FOLDER` is set to an absolute path.
- `saved` (bool): `True` if the file exists after capture.

**Restrictions:**
- `capture_image` must be its own protocol — do **not** mix it with `load_labware` or pipetting commands in the same protocol.
- Camera capture uses the V4L2 backend and is **Linux-only**.
- If no camera is configured, `capture_image` raises `RuntimeError` on the edge.
- Image format is always JPEG (`.jpg`).

### Custom Labware

- `mass_balance_vial_30000` and `mass_balance_vial_50000` are custom labware.
- These are automatically loaded via `protocol.load_labware_from_definition()` — the definition is embedded inline in the generated protocol code. No separate upload step is needed.

### Command Dependencies and Sequencing

**Important**: If the user's request contains invalid commands, incompatible labware, incorrect sequencing, or violates any constraints described in this document, **do not blindly follow the request**. Instead, identify the specific issue and clearly explain to the user what is wrong and why it cannot be executed.

**Critical sequencing rules:**
1. **`load_labware`** and **`load_instrument`**: Must come before all other commands.
2. **`home`**: Must be the first movement command, placed after all load commands.
3. **`pick_up_tip`**: Must be called before any `aspirate` or `dispense`. Only one tip at a time.
4. **`drop_tip`**: Must follow every `pick_up_tip`. Protocol must always end with no tip attached.
5. **`aspirate`** / **`dispense`**: May only occur after a tip has been picked up.
6. **`read_csv_file`** / **`read_csv`**: Must appear before the `loop` that uses its data.

## Instructions

1. **Consult Resources**: Consult the resources listed in the "Required Resources" section above before generating any commands.

2. **Verify sequencing and constraints**: **Always** verify that commands follow all rules in the "Rules and Restrictions" section, including: correct load order, `home` placement, `pick_up_tip` → pipetting → `drop_tip` sequencing so the protocol ends with no tip attached, valid deck slots, labware compatibility, volume constraints, and proper handling of missing information.

3. **Generate command**: Create a command object with `machine_id: "opentrons"`, appropriate `name` and `params`.
