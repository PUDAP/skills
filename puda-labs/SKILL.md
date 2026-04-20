---
name: puda-labs
description: Select the correct PUDA lab and load the matching machines and workflows skills based on the active profile.
---

# PUDA Labs

## Goal

Route to the correct lab-specific skills based on the active PUDA profile: `<profile_name>-machines` for machine capabilities and protocols, and `<profile_name>-workflows` for experiment workflows.

## Steps

1. Run `puda profile current` to get the active profile name.

2. The profile name maps to two skills:

   - `<profile_name>-machines` — machines, capabilities, protocol generation
   - `<profile_name>-workflows` — experiment workflows and which experiment to run

   Known labs: `bears`, `imre`, `ntu`

3. Read and follow the skills that match the task:

   | Lab   | Machines skill   | Workflows skill     |
   | ----- | ---------------- | ------------------- |
   | bears | `bears-machines` | `bears-workflows`   |
   | imre  | `imre-machines`  | `imre-workflows`    |
   | ntu   | `ntu-machines`   | `ntu-workflows`     |

4. If the required skill is not installed, stop and tell the user:

   > The `<profile_name>-machines` or `<profile_name>-workflows` skill is not installed. Install it using `puda skills install pudap/<profile_name>-skills` before continuing.

5. If the active lab does not have the machines needed for the task, tell the user:

   > The current lab (`<profile_name>`) may not have the machines required for this task. You might need to switch profiles before continuing.
