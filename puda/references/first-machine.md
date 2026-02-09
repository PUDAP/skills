---
name: first-machine
description: Generate commands for First machine liquid handling robots, including aspiration, dispensing, tip management, and deck configuration.
---

# First Machine Skills

Generate commands for First machine liquid handling robots.

## Purpose

This skill enables generation of commands for First machine liquid handling robots. These commands automate liquid handling operations including aspiration, dispensing, tip management, and deck configuration.

## When to Use

Load this skill when:
- Users describe protocols that need to be executed on liquid handling robots
- Converting manual lab protocols into automated puda protocols
- Processing natural language instructions for liquid handling operations
- Working with liquid handling workflows involving aspiration, dispensing, or tip management

## Required Resources

Before generating commands, consult the puda CLI:
- **Machine Help**: Use `puda machine first help` to see available commands and parameters

## Command Structure

Each First machine command follows the standard protocol command structure (see protocol-generator reference). Key First-specific details:

- `machine_id`: Must be `"first"` (string)
- `name`: Command name (e.g., `load_deck`, `attach_tip`, `aspirate_from`, `dispense_to`, `move_electrode`, `drop_tip`)
- `params`: Command-specific parameters (consult CLI help)
- `kwargs`: Optional keyword arguments

## Rules and Restrictions

The following rules must be **strictly followed** when generating First machine commands:

### Available Deck Slots
- **Valid deck slots**: A1, A2, A3, A4, B1, B2, B3, B4, C1, C2, C3, C4
- Use these slots for labware placement and operations

### Command Restrictions
- **`move_electrode` restriction**: Cannot use deck slots A1, B1 or C1
- **`height_from_bottom` constraint**: Must be non-negative (≥ 0)

### Command Dependencies and Sequencing

**Critical sequencing rules:**
1. **`load_deck`**: Must always be the **first** First machine command in any protocol. Use `puda machine first help labware` to discover available labware types and their parameters for the `load_deck` command.
2. **`attach_tip`**: Must be called before any `aspirate_from`, `dispense_to`, or `drop_tip` commands

**Labware compatibility:**
- **`aspirate_from`**: Can only be performed on `polyelectric_8_wellplate_30000ul` labware
- **`dispense_to`**: Can only be performed on:
  - `MEA_cell_MTP`
  - `polyelectric_8_wellplate_30000ul`
  - `trash_bin`
- **`attach_tip`**: Can only be performed on `tiprack` labware
- **`drop_tip`**: Can only be performed on `trash_bin` labware

### Common Command Flow Pattern
```
1. load_deck (required first)
2. attach_tip (required before liquid operations)
3. aspirate_from (from polyelectric_8_wellplate_30000ul)
4. dispense_to (to compatible labware)
5. drop_tip (to trash_bin)
```

## Instructions

1. **Consult CLI**: Run `puda machine first help` to review available commands and parameters

2. **Verify sequencing**: Ensure `load_deck` is ran before any commands and `attach_tip` precedes liquid operations

3. **Generate command**: Create a command object with `machine_id: "first"`, appropriate `name`, `params`, and optional `kwargs`

4. **Validate constraints**: Verify deck slots, non-negative `height_from_bottom`, and labware compatibility

## Best Practices

- **Sequencing**: Ensure `load_deck` is always the first First machine command, and `attach_tip` precedes liquid operations
- **Machine ID**: Always set `machine_id` to `"first"` (string)
- **Deck slots**: Use valid slots and respect restrictions (e.g., `move_electrode` cannot use A1-A4)
- **Constraints**: Ensure non-negative `height_from_bottom` and compatible labware types