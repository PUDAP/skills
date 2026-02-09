---
name: protocol-generator
description: Generate puda protocols using the puda CLI. Use when users need to create, validate, and send protocol commands to machines
---

# PUDA Protocol Generator

Generate and send protocols using the puda CLI tool for machine automation via NATS.

## Purpose

This skill enables generation, validation, and transmission of protocol commands to machines using the puda CLI tool. Protocols are sent via NATS using the `puda nats protocol` command.

## When to Use

Load this skill when:
- Users want to generate puda protocols
- Validating protocol commands before execution
- Converting structured JSON command sequences into executable protocols

## Required Resources

Before generating or sending protocols, consult the puda CLI:
- **Protocol Help**: Run `puda nats protocol --help` for protocol operations
- **Machine Help**: Use `puda machine [machine-id] help` for machine-specific commands

## Protocol Structure

**Important**: A single protocol can contain commands for multiple machines. Each command specifies its own `machine_id`, allowing workflows that coordinate operations across different machines (e.g., liquid handling followed by electrochemical testing). Step numbers are sequential across all commands regardless of which machine they target.

Protocols consist of structured JSON command sequences. Each command typically includes:
- `step_number`: Sequential integer starting from 1 (increments across all commands regardless of machine)
- `name`: Command name
- `machine_id`: ID of the target machine for this specific command (e.g., `"first"`, `"biologic"`)
- `params`: Command-specific parameters
- `kwargs`: Optional keyword arguments

## Instructions

1. **Consult CLI**: Run `puda nats protocol --help` and `puda machine [machine-id] help` for relevant machines

2. **Generate Protocol**: Create JSON structure with sequential step numbers, correct `machine_id` for each command, and valid command names/parameters

3. **Validate**: Use `puda nats protocol validate -f <file_name>` before sending

4. **Send**: Use `puda nats protocol` with appropriate flags to send via NATS

## Output Format

Return the answer as a valid JSON with the following structure. **Note: A protocol can contain commands for multiple machines** - each command specifies its own `machine_id`:

```json
{
  "user_id": "zhao",
  "username": "zhao",
  "description": "description for this protocol",
  "commands": [
    {
        "step_number": 1,
        "name": "load_deck",
        "machine_id": "first",
        "params": {
            "labware": {...}
        }
    },
    {
        "step_number": 2,
        "name": "OCV",
        "machine_id": "biologic",
        "params": {
            "time": 60,
            "time_interval": 1,
            "voltage_interval": 0.01
        },
        "kwargs": {
            "channels": [0],
            "retrieve_data": true
        }
    }
  ]
}
```

Each command object must include:
- `step_number`: Sequential integer starting from 1 (increments across all commands, regardless of machine)
- `name`: Valid command name from the available commands for the specified machine
- `machine_id`: ID of the machine the command is being sent to (e.g., `"first"`, `"biologic"`)
- `params`: Object containing all required and optional parameters for the specific command
- `kwargs`: Optional object containing additional keyword arguments (channels, retrieve_data, data, by_channel, cv, folder, etc.)



## Best Practices

- **Multi-machine support**: Protocols can contain commands for multiple machines - ensure each command has the correct `machine_id` (`"first"` or `"biologic"`)
- **Sequential steps**: Step numbers must be sequential (1, 2, 3...) across all commands regardless of machine
- **Validate first**: Always validate protocol structure before sending
- **Command dependencies**: Respect dependencies (e.g., `load_deck` first for First machine, `attach_tip` before liquid operations)

