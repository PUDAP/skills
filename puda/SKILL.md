---
name: puda
description: Skills and capabilities for working on the PUDA platform, including protocol generation, machine automation, and multi-machine workflow coordination
---

# PUDA Skills

This collection provides comprehensive skills and references for working with the PUDA platform, enabling automated machine control, protocol generation, and coordination of multi-machine workflows via NATS messaging.

## Overview

PUDA (Platform for Unified Device Automation) enables automated control of laboratory equipment including:
- **First Machine**: Liquid handling robots for aspiration, dispensing, and tip management
- **Biologic Machine**: Electrochemical testing devices for battery and cell characterization

Protocols can coordinate operations across multiple machines, enabling complex automated workflows.

## Setup Requirements

**CRITICAL - MUST BE EXECUTED AUTOMATICALLY**: Before using any puda skills:

1. **Driver Installation**: **MUST** automatically install or update `puda-drivers` to the latest version:
   ```bash
   pip install --upgrade puda-drivers
   ```

2. **Verification**: Confirm installation success before proceeding with any puda operations

3. **Timing**: This installation check and update must happen automatically before any other operations - do not proceed until `puda-drivers` is confirmed to be installed and up-to-date

## Tool Use Skill: puda CLI

You have access to the puda CLI tool. Follow this systematic approach to use it successfully:

### Discovery Workflow

1. **Explore Top Level**: Always start by running `puda -h` or `puda --help` to see available modules and top-level commands

2. **Drill Down**: Use `puda [subcommand] --help` to find specific flags and options for the task at hand

3. **Machine-Specific Help**: For machine operations, use `puda machine [machine-id] help` to see:
   - Available commands for that machine
   - Command-specific parameters and requirements
   - Optional keyword arguments (kwargs)

4. **Protocol Operations**: Use `puda nats protocol --help` to understand protocol generation, validation, and transmission options

### Validation and Safety

- **Flag Verification**: Before suggesting or running any command, verify that the flags you are using exist in the help documentation
- **Parameter Validation**: Check parameter requirements and constraints before generating commands
- **Protocol Validation**: Always validate protocol structure using `puda nats protocol validate -f <file_name>` before sending

### Output Handling

- **Parse Output**: Parse the output of puda commands to confirm success or extract IDs/values needed for subsequent steps
- **Error Detection**: Check for error messages or warnings in command output
- **Status Confirmation**: Verify that operations completed successfully before proceeding

## Workflow Patterns

### Single-Machine Protocol
Generate protocols that target a single machine (e.g., only First machine or only Biologic machine).

### Multi-Machine Protocol
Generate protocols that coordinate operations across multiple machines:
- Each command specifies its own `machine_id`
- Step numbers are sequential across all commands regardless of machine
- Enables workflows like: liquid handling → electrochemical testing

### Protocol Lifecycle
1. **Generate**: Create protocol JSON structure with appropriate commands
2. **Validate**: Use `puda nats protocol validate` to check structure
3. **Send**: Transmit via NATS using `puda nats protocol`
4. **Monitor**: Parse output to confirm successful transmission and execution

## References

- **[protocol-generator](references/protocol-generator.md)** - Generate, validate, and send puda protocols using the puda CLI. Essential for creating multi-machine workflows.
- **[first-machine](references/first-machine.md)** - Generate commands for First machine liquid handling robots, including deck configuration, tip management, and liquid operations.
- **[biologic-machine](references/biologic-machine.md)** - Generate commands for Biologic electrochemical testing devices, including OCV, CA, PEIS, GEIS, CV, and MPP tests.

## Best Practices

- Always consult the puda CLI help documentation before generating commands
- Validate protocols before sending them
- Ensure proper command sequencing (e.g., `load_deck` before other First machine commands)
- Use appropriate machine IDs (`"first"` or `"biologic"`) for each command
- Maintain sequential step numbers across all commands in multi-machine protocols
- Parse command output to verify success and extract necessary information
