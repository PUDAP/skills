---
name: puda-machines
description: Discover PUDA machine capabilities and choose the right machines for protocol generation. Use when you need to know more about a machine or how to use a machine.
---

# PUDA Machines

## Goal

Provide machine-selection and capability guidance for PUDA workflows, then load the correct machine reference before generating commands.

## Critical Rule

If you are unsure which machine should be used for a command, **ask the user** before proceeding.  
Do **not** assume.

## Machine Capabilities and When to Use

### First Machine (`machine_id: "first"`)

Use for **liquid handling and deck operations**.

Capabilities:
- Pipetting workflows: aspirate, dispense, attach tip, drop tip
- Deck and labware workflows: load deck, position-dependent operations
- Sequenced robotic handling steps in wet-lab protocols

Use this machine when:
- The task is about moving liquids between wells/labware
- The user mentions tip usage, aspiration/dispensing, or deck slots/labware setup

Before command generation:
- Refer to: [first-machine](references/first-machine.md)
- Run `puda machine commands first` to understand available commands
- Follow constraints and sequencing in `references/first-machine.md`

### Biologic Machine (`machine_id: "biologic"`)

Use for **electrochemical testing and characterization**.

Capabilities:
- OCV (Open Circuit Voltage)
- CA (Chronoamperometry)
- PEIS / GEIS (Impedance spectroscopy)
- CV (Cyclic Voltammetry)
- MPP variants (MPP, MPP_Cycles, MPP_Tracking)

Use this machine when:
- The task is an electrochemical measurement or battery/cell characterization
- The user asks for OCV, CA, EIS, CV, or MPP tests

Before command generation:
- Refer to: [biologic-machine](references/biologic-machine.md)
- Run `puda machine commands biologic` to understand available commands
- Follow constraints in `references/biologic-machine.md`

### Centrifuge Machine (`machine_id: "centrifuge"`)

Use for **centrifugation, spin-downs, and phase or pellet separation**.

Capabilities:
- Sample spin-downs before or after handling steps
- Separation workflows based on centrifugal force
- Pelleting, clarification, and phase-separation preparation steps

Use this machine when:
- The user asks to centrifuge, spin, spin down, pellet, or clarify samples

Before command generation:
- Refer to: [centrifuge-machine](references/centrifuge-machine.md)
- Run `puda machine commands centrifuge` to understand available commands
- Follow constraints in `references/centrifuge-machine.md`



## Selection Workflow

1. Parse user intent and identify the tasks.
2. Match intent to the machine capabilities above.
3. If machine selection is unclear or ambiguous, **ask the user** and wait for confirmation.
4. Load the corresponding reference file and CLI help.
5. Generate commands only after machine choice is confirmed.

## Output Guidance

When answering machine-selection questions:
- State the recommended machine and a one-line reason tied to capability.
- If uncertain, ask a direct clarification question instead of guessing.