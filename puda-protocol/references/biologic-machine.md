---
name: biologic-machine
description: Generate commands for Biologic electrochemical testing devices, including OCV, CA, PEIS, GEIS, CV, and MPP tests.
---

# Biologic Machine Skills

Generate commands for Biologic electrochemical testing devices.

## Purpose

This skill enables generation of commands for Biologic electrochemical testing devices. These commands automate electrochemical measurements including Open Circuit Voltage (OCV), Chronoamperometry (CA), Electrochemical Impedance Spectroscopy (PEIS, GEIS), Cyclic Voltammetry (CV), and Maximum Power Point tracking (MPP).

## When to Use

Load this skill when:
- Users describe electrochemical testing protocols (OCV, CA, PEIS, GEIS, CV, MPP)
- Converting manual electrochemical test procedures into automated puda protocols
- Processing natural language instructions for electrochemical measurements
- Working with battery or electrochemical cell characterization

## Required Resources

Before generating commands, consult the puda CLI:
- **Machine Help**: Use `puda machine commands biologic` to see available commands, parameters, and options

## Command Structure

Each Biologic machine command follows the standard protocol command structure (see protocol-generator reference). Key Biologic-specific details:

- `machine_id`: Must be `"biologic"` (string)
- `name`: One of the available test methods:
  - `OCV` - Open Circuit Voltage
  - `CA` - Chronoamperometry
  - `PEIS` - Potentiostatic Electrochemical Impedance Spectroscopy
  - `GEIS` - Galvanostatic Electrochemical Impedance Spectroscopy
  - `CV` - Cyclic Voltammetry
  - `MPP` - Maximum Power Point
  - `MPP_Cycles` - Maximum Power Point with cycles
  - `MPP_Tracking` - Maximum Power Point tracking
- `params`: Test-specific parameters (consult CLI help for each test type)

## Required Parameters

- **`channels`**: Must always be `[0]` (required for all Biologic commands)

## Instructions

1. **Consult CLI**: Run `puda machine commands biologic` to review available commands and their parameters

2. **Identify test type**: Choose the appropriate test method based on requirements (OCV, CA, PEIS, GEIS, CV, MPP variants)

3. **Generate command**: Create a command object with `machine_id: "biologic"`, appropriate `name` and `params`

4. **Validate**: Ensure `channels: [0]` is in params and all required parameters are present

## Best Practices

- **Required channels**: Always set `channels: [0]` in params
- **Machine ID**: Always set `machine_id` to `"biologic"` (string)
- **Test selection**: Choose the appropriate test method based on measurement requirements
- **Parameter completeness**: Include all required parameters for each test type in `params`
