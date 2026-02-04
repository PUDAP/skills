---
name: command-generator
description: Generate structured JSON commands for the First machine liquid handling robot from natural language lab instructions. Use when users need to convert lab workflows into executable First machine command sequences.
---

# First Machine Protocol Generator

Convert natural language lab protocol instructions into structured JSON commands for First machine liquid handling automation.

## Purpose

This skill enables conversion of natural language laboratory protocol descriptions into structured JSON command sequences that can be executed on First machine liquid handling robots.

## When to Use

Load this skill when:
- Users describe lab workflows that need to be executed on liquid handling robots
- Converting manual lab protocols into automated command sequences
- Generating structured JSON commands for First machine automation
- Processing natural language instructions for liquid handling operations

## Required Resources

Before generating any commands, consult the following scripts to understand available capabilities:

- **scripts/available-labware.py** - Lists all available labware types and their specifications
- **scripts/available-commands.py** - Describes all available commands, their parameters, and usage

**Important**: Before running these scripts, ensure the required Python packages are installed. 

### Rules and Restrictions

The following rules must be followed when generating commands:

**Available Deck Slots:**
- The following deck slots can be used: A1, A2, A3, A4, B1, B2, B3, B4, C1, C2, C3, C4

**Command Restrictions:**
- The `move_electrode` command cannot use deck slots A1, A2, A3, or A4
- The param `height_from_bottom` cannot be negative

**Command Dependencies:**
- `load_deck` must always be the first command in any protocol
- `attach_tip` must be called before any `aspirate_from`, `dispense_to`, or `drop_tip` commands
- `aspirate_from` can only be performed on `polyelectric_8_wellplate_30000ul` labware
- `dispense_to` can only be performed on the following labware types: `MEA_cell_MTP`, `polyelectric_8_wellplate_30000ul`, or `trash_bin`
- `attach_tip` can only be performed on `tiprack` labware
- `drop_tip` can only be performed on `trash_bin` labware

## Instructions

To generate a protocol from natural language instructions:

1. **Install dependencies**: Ensure the required Python package `puda_drivers` is installed by running `pip install puda_drivers` before executing any scripts.

2. **Consult resources first**: Run the available-labware.py and available-commands.py scripts to review labware types and command specifications before generating any protocol.

3. **Follow rules**: Adhere to command rules specified in the rules section above. Order commands correctly based on their dependencies.

4. **Validate parameters**: Ensure all command parameters match the specifications from the available-commands.py script and that labware references exist in the available-labware.py output.

5. **Check slot restrictions**: Verify that deck slots used in commands are in the available_slots list and respect any command_restrictions.

6. **Return structured JSON**: Output a valid JSON array of command objects.

## Output Format

Return the answer as a valid JSON array of command objects with the following structure:

```json
[
    {
        "step_number": 1,
        "name": "command_name",
        "params": {
            "param1": "value1",
            "param2": "value2"
        }
    }
]
```

Each command object must include:
- `step_number`: Sequential integer starting from 1
- `name`: Valid command name from the commands resource
- `params`: Object containing all required and optional parameters for the command

## Best Practices

- Always run the available-labware.py and available-commands.py scripts before generating protocols
- Validate all labware references against the labware script output
- Ensure command ordering respects dependency rules in the rules section
- Check that deck slots are valid and respect command restrictions
- Use clear, descriptive parameter values
- Include all required parameters for each command
