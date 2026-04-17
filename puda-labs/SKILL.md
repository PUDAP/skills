---
name: puda-labs
description: Select the correct PUDA lab and load the matching machines skill based on the active profile.
---

# PUDA Labs

## Goal

Route to the correct lab-specific machines skill based on the active PUDA profile.

## Steps

1. Run `puda profile current` to get the active profile name.

2. The profile name maps to a skill named `<profile_name>-machines`.

   Known labs: `bears`, `imre`, `ntu`

3. Read and follow the corresponding skill:
   - `bears` → use the `bears-machines` skill
   - `imre` → use the `imre-machines` skill
   - `ntu` → use the `ntu-machines` skill

4. If the required skill is not installed, stop and tell the user:

   > The `<profile_name>-machines` skill is not installed. Install it using `puda skills install <profile_name>-skills` before continuing.

5. If the active lab does not have the machines needed for the task, tell the user:

   > The current lab (`<profile_name>`) may not have the machines required for this task. You might need to switch profiles before continuing.
