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

Before generating commands, **always** consult the puda CLI:
- **Labware Help**: Use `puda machine first help labware` to see available labware and wells
- **Commands Help**: Use `puda machine first help commands` to see available commands and parameters

## Command Structure

Each First machine command follows the standard protocol command structure (see protocol-generator reference). Key First-specific details:

- `machine_id`: Must be `"first"` (string)

## Rules and Restrictions

The following rules **must** be strictly followed when generating First machine commands:

### Handling Missing Information

- If any information is missing from the user's request, **do not assume or guess values**. Use a placeholder value (e.g., `"PLACEHOLDER"` or `"?"`) in the command and explicitly ask the user to provide the missing information.
- If the labware only has one well (e.g., "A1"), then it is safe to assume that well name is "A1" without asking the user

### Available Deck Slots
- **Valid deck slots**: A1, A2, A3, A4, B1, B2, B3, B4, C1, C2, C3, C4
- Use these slots for labware placement and operations

### Command Restrictions
- **`move_electrode` restriction**: Cannot use deck slots A1, B1 or C1
- **`height_from_bottom` constraint**: Must be non-negative (≥ 0)

### Command Dependencies and Sequencing

**Important**: If the user's request contains invalid commands, incompatible labware, incorrect sequencing, or violates any constraints described in this document, **do not blindly follow the request**. Instead, identify the specific issue and clearly explain to the user what is wrong and why it cannot be executed.

**Critical sequencing rules:**
1. **`home`**: Must always be the **very first** First machine command in any protocol, before any other operations
2. **`load_deck`**: Must always be executed after `home` and before any other First machine commands. Use `puda machine first help labware` to discover available labware types and the required parameters
3. **`attach_tip`**: Must be called before any `aspirate_from`, `dispense_to`, or `drop_tip` commands

**Labware compatibility:**
- **`aspirate_from`**: Can only be performed on `polyelectric_8_wellplate_30000ul` labware
- **`dispense_to`**: Can only be performed on:
  - `MEA_cell_MTP`
  - `polyelectric_8_wellplate_30000ul`
  - `trash_bin`
- **`attach_tip`**: Can only be performed on `tiprack` labware
- **`drop_tip`**: Can only be performed on `trash_bin` labware

## Instructions

1. **Consult CLI**: Run `puda machine first help` to review available commands and parameters

2. **Verify sequencing**: Follow the critical sequencing rules in the "Command Dependencies and Sequencing" section above

3. **Generate command**: Create a command object with `machine_id: "first"`, appropriate `name`, `params`, and optional `kwargs`

4. **Validate constraints**: Verify deck slots, non-negative `height_from_bottom`, and labware compatibility

## Best Practices

- **Machine ID**: Always set `machine_id` to `"first"` (string)
- **Deck slots**: Use valid slots and respect restrictions (e.g., `move_electrode` cannot use A1-A4)
- **Constraints**: Ensure non-negative `height_from_bottom` and compatible labware types
- **Sequencing**: Refer to the "Command Dependencies and Sequencing" section for required command order