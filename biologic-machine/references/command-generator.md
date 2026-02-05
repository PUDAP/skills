---
name: command-generator
description: Generate structured JSON commands for Biologic electrochemical testing devices from natural language lab instructions. Use when users need to convert electrochemical test workflows into executable Biologic device command sequences.
---

# Biologic Machine Command Generator

Convert natural language electrochemical test protocol instructions into structured JSON commands for Biologic device automation.

## Purpose

This skill enables conversion of natural language laboratory protocol descriptions into structured JSON command sequences that can be executed on Biologic electrochemical testing devices.

## When to Use

Load this skill when:
- Users describe electrochemical test workflows that need to be executed on Biologic devices
- Converting manual electrochemical test protocols into automated command sequences
- Generating structured JSON commands for Biologic device automation
- Processing natural language instructions for electrochemical testing operations (OCV, CA, PEIS, GEIS, CV, MPP, etc.)

## Required Resources

Before generating any commands, consult the following script to understand available capabilities:

- **scripts/available-commands.py** - Describes all available commands, their parameters, and usage

## Available Commands

The BiologicMachine supports the following electrochemical test methods:

- **OCV** - Open Circuit Voltage test
- **CA** - Chronoamperometry test
- **CP** - Chrono-Potentiometry test
- **PEIS** - Potentiostatic Electrochemical Impedance Spectroscopy
- **GEIS** - Galvanostatic Electrochemical Impedance Spectroscopy
- **CV** - Cyclic Voltammetry test
- **MPP_Tracking** - Maximum Power Point Tracking
- **MPP** - Maximum Power Point test (includes CV scan and Voc scan)
- **MPP_Cycles** - MPP tracking with periodic CV scans

## Command Structure

Each command requires:
- **command_name**: One of the available test methods listed above
- **params**: Dictionary containing test-specific parameters
- **kwargs**: Optional keyword arguments (channels, retrieve_data, etc.)

## Instructions

To generate a protocol from natural language instructions:

1. **Install dependencies**: Ensure the required Python package `easy_biologic` is installed and that the BiologicMachine class is accessible.

2. **Consult resources first**: Run the available-commands.py script to review command specifications and parameter requirements before generating any protocol.

3. **Identify test type**: Determine which electrochemical test method is appropriate based on the user's requirements (OCV, CA, PEIS, GEIS, CV, MPP, etc.).

4. **Extract parameters**: Parse the natural language instructions to extract:
   - Test method name
   - Test-specific parameters (time, voltage, current, frequencies, etc.)
   - **Required parameters**: All parameters without default values must be explicitly provided
   - kwargs (channels, retrieve_data)

5. **Validate parameters**: Ensure all command parameters match the specifications from the available-commands.py script.

6. **Return structured JSON**: Output a valid JSON array of command objects.

## Output Format

Return the answer as a valid JSON array of command objects with the following structure:

```json
[
    {
        "step_number": 1,
        "name": "OCV",
        "machine_id": "biologic",
        "params": {
            "time": 60,
            "time_interval": 1,
            "voltage_interval": 0.01
        },
        "kwargs": {
            "channels": [0],
            "retrieve_data": true
        }
    }
]
```

Each command object must include:
- `step_number`: Sequential integer starting from 1
- `name`: Valid command name from the available commands
- `machine_id`: ID of the machine the command is being sent to
- `params`: Object containing all required and optional parameters for the specific test method
- `kwargs`: Optional object containing additional keyword arguments (channels, retrieve_data, data, by_channel, cv, folder, etc.)

## Parameter Notes

### Common Parameters Across Tests

- **channels**: Must always be `[0]` (required)

### Test-Specific Parameters

Each test method has specific parameter requirements. Consult the available-commands.py script for detailed parameter specifications for each test type.

### Special Command Requirements

- **MPP and MPP_Cycles**: Support additional kwargs: `data`, `by_channel`, `cv`
- **MPP_Tracking**: Supports additional kwargs: `folder`, `by_channel`
- **Standard programs** (OCV, CA, PEIS, GEIS, CV): Support `retrieve_data` kwarg

## Best Practices

- Always run the available-commands.py script before generating protocols
- Validate all parameters against the command specifications
- **Always set channels to `[0]` in kwargs** - this is required for all commands
- Use appropriate test method based on the electrochemical measurement requirements
- Include all required parameters for each test type
- Use clear, descriptive parameter values with appropriate units (seconds, Volts, Amperes, Hertz, etc.)

