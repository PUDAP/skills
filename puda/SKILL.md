---
name: puda
description: Skills for using the puda CLI tool to generate protocols, interact with machines, and manage automated workflows
---

# PUDA CLI Skills

This collection provides skills for using the puda CLI tool to interact with laboratory automation equipment, generate protocols, and manage machine operations.

## Setup Requirements

**CRITICAL - MUST BE EXECUTED AUTOMATICALLY**: Before using any puda CLI commands:

1. **Driver Installation**: **MUST** automatically install or update `puda-drivers` to the latest version:
   ```bash
   pip install --upgrade puda-drivers
   ```

2. **Verification**: Confirm installation success before proceeding with any puda CLI operations

3. **Timing**: This installation check and update must happen automatically before any other operations - do not proceed until `puda-drivers` is confirmed to be installed and up-to-date

## Using the puda CLI

You have access to the puda CLI tool. Follow this systematic approach to use it successfully:

### Discovery Workflow

1. **Explore Top Level**: Always start by running `puda -h` or `puda --help` to see available modules and top-level commands

2. **Drill Down**: Use `puda [subcommand] --help` to find specific flags and options for the task at hand

3. **Machine-Specific Help**: For machine operations, always use `puda machine [machine-id] help` for more context

4. **Protocol Operations**: Use `puda nats protocol --help` to understand protocol generation, validation, and transmission options

### Validation and Safety

- **Flag Verification**: Before suggesting or running any command, verify that the flags you are using exist in the help documentation
- **Parameter Validation**: Check parameter requirements and constraints before generating commands
- **Protocol Validation**: Always validate protocol structure using `puda nats protocol validate -f <file_name>` before sending

### Output Handling

- **Parse Output**: Parse the output of puda commands to confirm success or extract IDs/values needed for subsequent steps
- **Error Detection**: Check for error messages or warnings in command output
- **Status Confirmation**: Verify that operations completed successfully before proceeding

## References

- **[protocol-generator](references/protocol-generator.md)** - Generate, validate, and send puda protocols using the puda CLI
- **[first-machine](references/first-machine.md)** - Generate commands for First machine liquid handling robots using the puda CLI
- **[biologic-machine](references/biologic-machine.md)** - Generate commands for Biologic electrochemical testing devices using the puda CLI

## Best Practices

- **Always consult CLI help**: Run `puda [subcommand] --help` before executing commands to verify available flags and options
- **Use machine-specific help**: Run `puda machine [machine-id] help` to discover available commands, labware, and parameters
- **Validate before sending**: Use `puda nats protocol validate` to check protocol structure before transmission
- **Parse output**: Extract information from command output to verify success and gather necessary data
