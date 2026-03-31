---
name: puda-protocol
description: Protocol creation for PUDA. Use when doing anything related to PUDA protocols
---

## Constraint

**Must call the puda-memory skill immediately after creating or updating a protocol file.** That skill keeps **project.md** as the source of truth; it will append the new protocol link and history entry.

---

## Protocol Structure

A single protocol can contain commands for **multiple machines**. Each command specifies its own `machine_id`. Step numbers are sequential across all commands regardless of machine.

Top-level fields:
- `project_id`: UUID from **project.md** in the project root
- `protocol_id`: New UUID per protocol (e.g. `python -c "import uuid; print(uuid.uuid4())"`)
- `user_id`, `username`: From `puda config list`
- `description`: Short description of what the protocol does
- `timestamp`: ISO 8601 UTC (e.g. `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`)
- `commands`: Array of command objects (see below)

Each command:
- `step_number`: Sequential integer from 1 (across all commands)
- `name`: Valid command name for the specified machine
- `machine_id`: Target machine id
- `params`: Required and optional parameters for the command

## Command Generation

**CRITICAL**: Before generating commands, invoke the **puda-machines** skill to read the relevant machine reference and commands

**CRITICAL**: If you are unsure of which machine to use for a certain task, ask the user before proceeding

## Instructions

1. **Ensure project exists**: If there is no project yet, ask the user for the project name and description before continuing, then run `puda project create` to create the project folder.
2. **User info**: Run `puda config list` for `user_id` and `username`.
3. **Protocol ID and timestamp**: Generate UUID and ISO datetime (e.g. via Python `uuid.uuid4()` and `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`).
4. **Machine references**: Use `puda-machines` skill to understand the machines and available commands.
5. **Generate**: Create a new JSON file under the project's `protocols/` directory. Filename = `protocol_id.json`. When modifying a protocol, **always create a new file and new `protocol_id`**; do not overwrite.
6. **Validate**: Run `puda protocol validate -f <file_name>` to validate the protocol.
7. **Update project memory**: **Must** invoke the **puda-memory** skill right after creating/updating the file so `project.md` is updated.

## Output Format (JSON)

```json
{
  "project_id": "<project_id>",
  "protocol_id": "<protocol_id>",
  "user_id": "<from puda config list>",
  "username": "<from puda config list>",
  "description": "description for this protocol",
  "timestamp": "<ISO 8601>",
  "commands": []
}
```

Each command: `step_number`, `name`, `machine_id`, `params`

## Troubleshooting

- **RUN_ID_MISMATCH** when sending a protocol file: run `puda machine reset <machine_id>` to reset the machine, then send the protocol again.

## Best Practices

- Never overwrite or reuse an existing protocol file or id; always create a new file and new protocol_id when modifying.
- Multi-machine: each command must have the correct `machine_id`; steps stay sequential (1, 2, 3, …).
- Always validate after creating; fix any errors before sending.
- After writing the file, **always** call **puda-memory** to update `project.md`.
