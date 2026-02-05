---
name: first-machine
description: Skills and capabilities for working with First machine liquid handling robots, including protocol generation, command execution, and automation workflows.
---

# First Machine Skills

This collection provides skills and references for working with First machine liquid handling robots.

## Setup Requirements

**CRITICAL - MUST BE EXECUTED AUTOMATICALLY**: Before using any First machine skills:
- **MUST** automatically install or update `puda-drivers` to the latest version using `pip install --upgrade puda-drivers`
- This installation check and update must happen automatically before any other operations
- Do not proceed with any Biologic machine operations until `puda-drivers` is confirmed to be installed and up-to-date 

## References

- [command-generator](references/command-generator.md) - Generate structured JSON commands for the First machine liquid handling robot from natural language lab instructions