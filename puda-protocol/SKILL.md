---
name: puda-protocol
description: Create, edit, validate, and run PUDA protocol JSON, including multi-machine steps, delays, and live command safety metadata. Use when planning or executing PUDA protocols.
---

# PUDA protocols

Create or update protocol JSON under the project's `protocols/` directory. Reuse existing protocols when appropriate; create a new file when requested or needed.

## Workflow

1. Check authentication and the project. If login is missing, ask the user to log in. For a new project, obtain its name and description, then use `puda init`.
2. Read [protocol format](references/format.md) for fields, IDs, timestamps, parallel steps, and CLI-only `wait` commands. Use the project UUID from `project.md`; generate a new protocol UUID and real UTC timestamp for a new protocol.
3. Discover machines with `puda machine list`; consult machine references and previous protocols. Fetch `puda machine commands <machine_id>` for every machine command used. Ask the user if the correct machine or command remains unclear. Do not look up `wait` on a machine.
4. Copy every advertised safety object unchanged. Follow its `requires` and `forbidden_when` conditions. Read [safety and execution](references/safety-and-execution.md) when handling safety metadata or running a protocol.
5. Write `protocols/<protocol_id>.json`. Immediately use **puda-memory** to update `project.md` after creating or editing the file.
6. Run `puda protocol validate -f <file_name>`; success must be exactly `passed`. Fix errors and repeat validation. Use the relevant machine's `puda-vision-validation` skill when available.
7. When executing the protocol, honor confirmation gates and record the run through **puda-memory**.

## Invariants

- Commands sharing a `step_number` run in parallel; never repeat a `machine_id` in that group.
- `wait` is handled by the CLI, never dispatched to hardware. Omit its `machine_id` for a protocol-wide pause; set it for a machine-specific pause.
- Safety metadata must match the live catalog, including all fields; refresh it after edits.
- At a `confirm: true` gate, show the operator the complete displayed commands and safety context, then wait for explicit approval before submitting `yes`. Parallel commands share one gate. Prompt only when the catalog sets `confirm: true`; reject or terminate if approval is denied.
