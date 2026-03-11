---
name: puda-protocol
description: Protocol creation for PUDA. Use when generating or modifying protocols for experiments and discovering machine capabilities
---

# Puda Protocol Generation

## Goal

Machine discovery and protocol creation: discover machine capabilities via the puda CLI and generate valid JSON protocols for the experiment’s **protocols/** directory.

## Logic

1. **Machine discovery**: Use puda machine commands to see capabilities (e.g. `puda machine first commands`). Use this to determine valid command names, parameters, and labware.
2. **Protocol generation**: User info, protocol ID/datetime, machine references, JSON structure (below), validation with `puda protocol validate -f <file>`.
3. Save protocol files under the experiment’s **protocols/** directory; filename = `protocol_id.json`.

## Constraint

**Must call the puda-memory skill immediately after creating or updating a protocol file.** That skill keeps **experiment.md** as the source of truth; it will append the new protocol link and history entry.

---

## Protocol Structure

A single protocol can contain commands for **multiple machines**. Each command specifies its own `machine_id`. Step numbers are sequential across all commands regardless of machine.

Top-level fields:
- `experiment_id`: UUID from **experiment.md** in the experiment root
- `protocol_id`: New UUID per protocol (e.g. `python -c "import uuid; print(uuid.uuid4())"`)
- `user_id`, `username`: From `puda config list`
- `description`: Short description of what the protocol does
- `timestamp`: ISO 8601 UTC (e.g. `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`)
- `commands`: Array of command objects (see below)

Each command:
- `step_number`: Sequential integer from 1 (across all commands)
- `name`: Valid command name for the specified machine
- `machine_id`: Target machine (e.g. `"first"`, `"biologic"`)
- `params`: Required and optional parameters for the command
- `kwargs`: Optional (channels, retrieve_data, data, by_channel, cv, folder, etc.)

## Command Generation

**CRITICAL**: Before generating commands, read the relevant machine reference:
- First machine: [first-machine](references/first-machine.md)
- Biologic machine: [biologic-machine](references/biologic-machine.md)

## Instructions

1. **User info**: Run `puda config list` for user_id and username.
2. **Protocol ID and timestamp**: Generate UUID and ISO datetime (e.g. via Python `uuid.uuid4()` and `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`).
3. **Machine references**: Read the machine docs or CLI help for valid commands and params.
4. **Generate**: Create a new JSON file under the experiment’s **protocols/** directory. Filename = `protocol_id.json`. When modifying a protocol, **always create a new file and new protocol_id** — do not overwrite.
5. **Validate**: Run `puda protocol validate -f <file_name>` before sending using `puda protocol send -f <file_name>`.
6. **Update experiment**: **Must** invoke the **puda-memory** skill right after creating/updating the file so experiment.md is updated.

## Output Format (JSON)

```json
{
  "experiment_id": "<experiment_id>",
  "protocol_id": "<protocol_id>",
  "user_id": "<from puda config list>",
  "username": "<from puda config list>",
  "description": "description for this protocol",
  "timestamp": "<ISO 8601>",
  "commands": []
}
```

Each command: `step_number`, `name`, `machine_id`, `params`, `kwargs` (optional).

## Troubleshooting

- **RUN_ID_MISMATCH** when sending a protocol file: run `puda machine <machine_id> reset` to reset the machine, then send the protocol again.

## Best Practices

- Never overwrite or reuse an existing protocol file or id; always create a new file and new protocol_id when modifying.
- Multi-machine: each command must have the correct `machine_id`; steps stay sequential (1, 2, 3, …).
- Always validate after creating; fix any errors before sending.
- After writing the file, **always** call **puda-memory** to update experiment.md.
