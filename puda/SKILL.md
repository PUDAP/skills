---
name: puda
description: Skills for using the puda CLI tool to generate protocols, interact with machines, and manage automated workflows
---

# PUDA CLI Skills

This collection provides skills for using the puda CLI tool to interact with laboratory automation equipment, generate protocols, and manage machine operations.

## Setup Requirements

**CRITICAL - MUST BE EXECUTED AUTOMATICALLY**: Before using any puda CLI commands:

1. **Python and pip**: **MUST** Ensure `python3` and `pip` are installed. If not installed, install them before continuing execution

2. **Driver Installation**: **MUST** automatically install or update `puda-drivers` to the latest version:
   ```bash
   pip install --upgrade puda-drivers
   ```

3. **Verification**: Confirm installation success before proceeding with any puda CLI operations

## Updating puda skills

To refresh or update puda skills:

```bash
puda skills update
```

## Using the puda CLI

You have access to the puda CLI tool. Follow this systematic approach to use it successfully:

- **Machine-Specific Help**: For machine operations, always use `puda machine [machine-id] help` for more context

- **Protocol Operations**: Use `puda nats protocol` to understand protocol generation, validation, and transmission options

### Protocol Generation

**CRITICAL**: When generating protocols, **MUST** read the **[protocol-generator](references/protocol-generator.md)** reference document first. This document contains:
- Protocol structure requirements and format specifications
- Step numbering rules (sequential across all commands regardless of machine)
- Multi-machine protocol support details
- Required fields and command structure
- Validation procedures

Always consult the protocol-generator reference before creating any protocol JSON structure.

### Sending protocol

- Always use `puda nats protocol send -f <file_path>` to send nats protocol

### Validation and Safety

- **Flag Verification**: Before suggesting or running any command, verify that the flags you are using exist in the help documentation

### Output Handling

- **Parse Output**: Parse the output of puda commands to confirm success or extract IDs/values needed for subsequent steps
- **Error Detection**: Check for error messages or warnings in command output
- **Status Confirmation**: Verify that operations completed successfully before proceeding

## Experiment tracking

**CRITICAL**: Persist all experiment-related state so runs are reproducible and auditable.

- **Initialization**: Running `puda init` creates an **`experiment.md`** file in the project root. Use it as the single place to record everything about the current experiment.

- **What to record in `experiment.md`**:
  - **Logs**: Use explicit markdown links to log files, e.g. `[<run_id>](logs/<run_id>.log)`. Add a new log link each time a protocol is run.
  - **Protocols**: Use explicit markdown links to protocol files. In the "Protocols" section, list each as `[<protocol_id>](protocols/<protocol_id>.json)` with an optional short description after the link (e.g. `[<protocol_id>](protocols/<protocol_id>.json) — changed dispense amount to 100ul in step 10`).
  - **History**: A chronological log of actions with ISO 8601 timestamps. **MUST** use the actual current time for each entry—never guess or use a placeholder. Before writing a history line, run `date -u +%Y-%m-%dT%H:%M:%SZ` to get the real timestamp and use that value. Use explicit markdown links for all file paths. Append one line per action in this form:
    - `<timestamp> created [<protocol_id>](protocols/<protocol_id>.json)`
    - `<timestamp> updated [<old_protocol_id>](protocols/<old_protocol_id>.json) to [<new_protocol_id>](protocols/<new_protocol_id>.json)`
    - `<timestamp> ran [<protocol_id>](protocols/<protocol_id>.json) — logs: [<log_id>](logs/<log_id>.log)`

- **When to update**: After creating a protocol file, after updating/deriving a new protocol, and after every protocol run (append the run entry and the new log path).

## References

- **[database-query](references/database-query.md)** - Query database using SQL and puda cli
- **[protocol-generator](references/protocol-generator.md)** - Generate, validate, and send puda protocols using the puda CLI
- **[first-machine](references/first-machine.md)** - Generate commands for First machine liquid handling robots using the puda CLI
- **[biologic-machine](references/biologic-machine.md)** - Generate commands for Biologic electrochemical testing devices using the puda CLI

## Best Practices

- **Read protocol-generator reference**: **MUST** read the [protocol-generator](references/protocol-generator.md) reference document before generating any protocols to ensure correct structure and format
- **Always consult CLI help**: Run `puda [subcommand] --help` before executing commands to verify available flags and options
- **Use machine-specific help**: Run `puda machine [machine-id] help` to discover available commands, labware, and parameters
- **Validate before sending**: Use `puda nats protocol validate` to check protocol structure before transmission
- **Parse output**: Extract information from command output to verify success and gather necessary data
- **Update experiment tracking**: After creating/updating protocols or running them, append the action and any log path to `experiment.md` (and `protocol.json` if used) per the Experiment tracking section
