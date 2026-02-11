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

## References

- **[protocol-generator](references/protocol-generator.md)** - Generate, validate, and send puda protocols using the puda CLI
- **[first-machine](references/first-machine.md)** - Generate commands for First machine liquid handling robots using the puda CLI
- **[biologic-machine](references/biologic-machine.md)** - Generate commands for Biologic electrochemical testing devices using the puda CLI

## Best Practices

- **Read protocol-generator reference**: **MUST** read the [protocol-generator](references/protocol-generator.md) reference document before generating any protocols to ensure correct structure and format
- **Always consult CLI help**: Run `puda [subcommand] --help` before executing commands to verify available flags and options
- **Use machine-specific help**: Run `puda machine [machine-id] help` to discover available commands, labware, and parameters
- **Validate before sending**: Use `puda nats protocol validate` to check protocol structure before transmission
- **Parse output**: Extract information from command output to verify success and gather necessary data
