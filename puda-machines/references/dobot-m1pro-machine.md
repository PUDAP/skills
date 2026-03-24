---
name: dobot-m1pro-machine
description: Generate commands for Dobot M1Pro gripper workflows that transfer tubes between fixed hardcoded positions.
---

# Dobot M1Pro Machine Skills

Generate commands for Dobot M1Pro gripper-based tube transfer workflows.

## Purpose

This reference helps generate commands for Dobot M1Pro operations that use a gripper to pick up and move tubes between known positions in the workspace.

## When to Use

Load this reference when:
- Users ask to transfer tubes with a gripper
- A workflow needs pick-and-place tube movement between fixed positions
- The user refers to hardcoded Dobot M1Pro positions

## Required Resources

Before generating commands, consult the puda CLI:
- **Machine Help**: Use `puda machine commands dobot-m1pro` to see available commands, parameters, and options

Do not invent command names or parameters. If the CLI output does not expose a requested operation, explain that gap to the user instead of guessing.

## Command Structure

Each Dobot M1Pro machine command follows the standard protocol command structure (see protocol-generator reference). Key Dobot M1Pro details:

- `machine_id`: Must be `"dobot-m1pro"` (string)
- `name`: Must be a valid Dobot M1Pro command returned by `puda machine commands dobot-m1pro`
- `params`: Use only parameters supported by the CLI for that command

## Hardcoded Positions

Use these fixed positions exactly as defined when the workflow references them:

- `centrifuge-tube-mtp-a1`: `[287, -234, 5, -33]`
- `centrifuge-tube-mtp-d1`: `[287, -174, 5, -33]`
- `centrifuge-tube-mtp-a6`: `[182, -174, 5, -33]`

If the user requests a position that is not listed here, do not guess. Ask for the exact position or confirm whether one of the hardcoded positions should be used.

## Required Information

Before generating a Dobot M1Pro command, confirm:

- Which tube should be moved
- The source position
- The destination position

If required information is missing, do not assume it. Ask the user, or use an explicit placeholder only when the surrounding workflow requires drafting an incomplete command for review.

## Rules and Restrictions

Apply these rules when preparing Dobot M1Pro commands:

- Use only the hardcoded positions listed in this document unless the user provides another exact position
- Treat tube transfers as gripper-based pick-and-place operations
- Ask for missing source or destination details instead of guessing

## Instructions

1. **Consult CLI**: Run `puda machine commands dobot-m1pro` to review available commands and parameters.
2. **Match the operation**: Choose the Dobot M1Pro command that best matches the requested tube transfer.
3. **Resolve positions**: Use the hardcoded position names and coordinates from this document when applicable.
4. **Generate command**: Create a command object with `machine_id: "dobot-m1pro"`, a valid `name`, and supported `params`.

## Best Practices

- Prefer named hardcoded positions over repeating raw coordinates in explanations.
- Keep source and destination positions explicit in every transfer step.
- Ask for missing transfer details instead of guessing.
