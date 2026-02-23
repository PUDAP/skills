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

## Protocol Structure

**Important**: A single protocol can contain commands for multiple machines. Each command specifies its own `machine_id`, allowing workflows that coordinate operations across different machines (e.g., liquid handling followed by electrochemical testing). Step numbers are sequential across all commands regardless of which machine they target.

Protocols are structured JSON objects with the following top-level fields:
- `protocol_id`: UUID string
- `user_id`: User identifier string
- `username`: Username string
- `description`: Description of the protocol
- `timestamp`: ISO 8601 timestamp string 
- `commands`: Array of command objects

Each command object in the `commands` array includes:
- `step_number`: Sequential integer starting from 1 (increments across all commands regardless of machine)
- `name`: Command name (must be valid for the specified machine)
- `machine_id`: ID of the target machine for this specific command 
- `params`: Object containing all required and optional parameters for the specific command
- `kwargs`: Optional object containing additional keyword arguments 

## Command Generation

**CRITICAL**: When generating commands for a protocol, **MUST** read the relevant machine reference document first:
- For First machine commands: Read [first-machine](references/first-machine.md)
- For Biologic machine commands: Read [biologic-machine](references/biologic-machine.md)

These documents contain the available commands, required parameters, labware definitions, and machine-specific constraints that must be followed.

## Instructions

1. **Fetch User Info**: Run `puda config list` to get user_id and username

2. **Generate Protocol ID and datetime**: Run the following in Python to get both the protocol_id (UUID) and current datetime in ISO format:
   ```python
   import uuid
   from datetime import datetime, timezone
   print("protocol_id:", uuid.uuid4())
   print("datetime:", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
   ```

3. **Consult references**: Read the relevant machine documents for machine specific commands (see References section below)

4. **Generate Protocol**: Create a new JSON protocol file with the exact structure shown in the Output Format section. Save protocol files under the **`/protocols`** directory in the project root. The filename should be the protocol_id and must end with `.json` extension. **When modifying a protocol, always create a new protocol file and a new protocol_id** — do not overwrite or reuse an existing protocol file or id.

5. **Validate**: Use `puda nats protocol validate -f <file_name>` before sending

## Output Format

Return the answer as a valid JSON with the following structure. **Note: A protocol can contain commands for multiple machines** - each command **must** specifies its own `machine_id`:

```json
{
  "protocol_id": "<protocol_id>",
  "user_id": "zhao",
  "username": "zhao",
  "description": "description for this protocol",
  "timestamp": "<datetime>",
  "commands": []
}
```

Each command object must include:
- `step_number`: Sequential integer starting from 1 (increments across all commands, regardless of machine)
- `name`: Valid command name from the available commands for the specified machine
- `machine_id`: ID of the machine the command is being sent to (e.g., `"first"`, `"biologic"`)
- `params`: Object containing all required and optional parameters for the specific command
- `kwargs`: Optional object containing additional keyword arguments (channels, retrieve_data, data, by_channel, cv, folder, etc.)

## Best Practices

- **Modifying protocols**: Always create a new protocol file and a new protocol_id when modifying a protocol; never overwrite or reuse an existing protocol file or id.
- **Multi-machine support**: Protocols can contain commands for multiple machines - ensure each command has the correct `machine_id` (`"first"` or `"biologic"`)
- **Sequential steps**: Step numbers must be sequential (1, 2, 3...) across all commands regardless of machine
- **Validate**: Always validate protocol structure after creating it, fix any errors that appear
- **Command dependencies**: Respect dependencies for specific machines

## References

- **[first-machine](references/first-machine.md)** - Generate commands for First machine liquid handling robots
- **[biologic-machine](references/biologic-machine.md)** - Generate commands for Biologic electrochemical testing devices