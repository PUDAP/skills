---
name: puda-protocol
description: Protocol creation for PUDA. Use when doing anything related to PUDA protocols
---

## Constraint

**Must call the puda-memory skill immediately after creating or updating a protocol file.** That skill keeps **project.md** as the source of truth; it will append the new protocol link and history entry.

---

## Protocol Structure

A single protocol can contain commands for **multiple machines**. Each command specifies its own `machine_id`. Step numbers are sequential execution groups across all commands. If commands are meant to be executed in parallel, use the same `step_number`; however, `machine_id` cannot be repeated within the same parallel command group.

Top-level fields:
- `project_id`: UUID from **project.md** in the project root
- `protocol_id`: New UUID per protocol (e.g. `python -c "import uuid; print(uuid.uuid4())"`)
- `description`: Short description of what the protocol does
- `timestamp`: ISO 8601 UTC (e.g. `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`)
- `commands`: Array of command objects (see below)

Each command:
- `step_number`: Sequential integer from 1; commands with the same value execute in parallel
- `name`: Valid command name for the specified machine
- `machine_id`: Target machine id
- `params`: Required and optional parameters for the command
- `safety`: Required when the live command catalog advertises safety metadata; copy the structured metadata into the command unchanged

## Command Safety

After `puda machine commands <machine_id>`, treat any `safety:` block as required planning and execution context. When a command advertises safety metadata, copy it into that command in `protocol.json`. Do not invent, summarize, weaken, or omit any safety field. The live catalog remains the source of truth; refresh the copied metadata whenever the protocol is updated.

Canonical command shape:

```json
{
  "step_number": 1,
  "machine_id": "machine-001",
  "name": "move_to",
  "params": {
    "x": 1,
    "y": 1,
    "z": 1
  },
  "safety": {
    "summary": "Confirm the workspace is clear before moving.",
    "hazards": [
      "collision"
    ],
    "requires": "Machine must just have been homed and the workspace clear.",
    "forbidden_when": "Do not move if the workspace is occupied, human movement is detected",
    "confirm": true
  }
}
```

Safety field types are fixed:

- `summary`: string
- `hazards`: array of strings
- `requires`: string
- `forbidden_when`: string
- `confirm`: boolean

- Follow `requires` in the `safety:` block as prose: insert earlier steps or ask the user before using the command.
- Follow `forbidden_when` as prose: do not use the command when that situation applies.
- If `confirm` is `true`, `puda protocol run` prints the complete command and safety object for the current step, then blocks until `yes` is entered. The AI agent must present that exact output to the operator and wait for explicit approval. Do not submit `yes` first and ask later.
- Only prompt when the catalog explicitly shows `confirm: true`. `@safety` defaults `confirm` to `false`.
- For agent-driven execution, start `puda protocol run` with `terminal(background=true, pty=true, watch_patterns=["Type yes to continue step"])`. When the prompt appears, inspect the process output, show the complete command and safety context to the operator, and wait. After explicit approval, continue with `process(action="submit", data="yes")`. If permission is denied, submit any value other than `yes` or terminate the process. Parallel commands at the same step are displayed together and use one confirmation covering every safety-tagged command and machine in that step.

## Command Generation

**CRITICAL**: If you are unsure of which machine or command to use for a certain task, always ask or confirm with the user before proceeding

**CRITICAL**: Use `puda machine list` to see each online machine's advertised description. Use available machine references and previous protocols to understand valid machines, commands, and parameters. Fetch `puda machine commands <machine_id>` when you need signatures, parameters, or safety metadata.

**CRITICAL**: Make use of previous protocol files whenever possible unless user explicitly wants a new file to be generated. Skip the first 3 instructions if not needed

## Instructions

1. **Ensure user is logged in**: Check whether the user is authenticated with puda cli. If they are not, ask them to log in before proceeding.
2. **Ensure project exists**: If there is no project yet, ask the user for the project name and description before continuing, then use `puda init` to create the project folder.
3. **Protocol ID and timestamp**: Generate UUID and ISO datetime (e.g. via Python `uuid.uuid4()` and `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`).
4. **Machine references and safety**: Use `puda machine list` for each machine's advertised description. Use available machine references and previous protocols to understand the machines and available commands. Retrieve the live command definition for every command used. If the correct machine or command is unclear, ask or confirm with the user before proceeding. Copy every advertised safety object into its command.
5. **Generate**: Create a new JSON file under the project's `protocols/` directory. Filename = `<protocol_id>.json`.
6. **Validate**: Run `puda protocol validate -f <file_name>`. Success output must be exactly `passed`; otherwise fix every returned error and validate again.
7. **Vision Validation**: Use the respective `puda-vision-validation` skill for the relevant machine.
8. **Update project memory**: **Must** invoke the **puda-memory** skill right after creating/updating the file so `project.md` is updated.
9. **Execute with confirmation gates**: Run the protocol interactively. At every `Type yes to continue step ...` prompt, relay the complete displayed command and safety chunk to the operator. Submit `yes` only after explicit approval; otherwise reject or terminate the run.

## Output Format (JSON)

```json
{
  "project_id": "<project_id>",
  "protocol_id": "<protocol_id>",
  "description": "description for this protocol",
  "timestamp": "<ISO 8601>",
  "commands": []
}
```

Each command: `step_number`, `name`, `machine_id`, `params`, plus `safety` whenever the live command catalog advertises it.

## Troubleshooting

- **RUN_ID_MISMATCH** when sending a protocol file: run `puda machine reset <machine_id>` to reset the machine, then send the protocol again.

## Best Practices

- Multi-machine: each command must have the correct `machine_id`; use the same `step_number` only for parallel commands, and do not repeat a `machine_id` in the same step.
- Safety fidelity: copied safety metadata must match the live catalog exactly. A missing or changed field requires regenerating the command entry before execution.
- Confirmation: never start a `confirm: true` command or step group until the operator has explicitly approved the displayed safety context.
- Always validate after creating; fix any errors before sending.
- After writing the file, **always** call **puda-memory** to update `project.md`.
