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

Before generating any commands, consult the following MCP resources to understand available capabilities:

- **first://labware** - Lists all available labware types and their specifications
- **first://commands** - Describes all available commands, their parameters, and usage
- **first://rules** - Contains rules and restrictions including command dependencies and available slots

## Instructions

To generate a protocol from natural language instructions:

1. **Consult resources first**: Fetch and review the labware, commands, and rules resources before generating any protocol.

2. **Follow dependencies**: Adhere to command dependencies specified in the rules resource. Order commands correctly based on their dependencies.

3. **Validate parameters**: Ensure all command parameters match the specifications in the commands resource and that labware references exist in the labware resource.

4. **Return structured JSON**: Output a valid JSON array of command objects.

## Output Format

Return the answer as a valid JSON array of command objects with the following structure:

```json
[
    {
        "step_number": 1,
        "command": "command_name",
        "params": {
            "param1": "value1",
            "param2": "value2"
        }
    }
]
```

Each command object must include:
- `step_number`: Sequential integer starting from 1
- `command`: Valid command name from the commands resource
- `params`: Object containing all required and optional parameters for the command

## Best Practices

- Always fetch MCP resources before generating protocols
- Validate all labware references against the labware resource
- Ensure command ordering respects dependency rules
- Use clear, descriptive parameter values
- Include all required parameters for each command
