---
name: puda-env
description: Select the correct PUDA env and load the matching machines and workflows skills based on the active env.
---

# PUDA Envs

## Goal

Route to the correct env-specific skills based on the active PUDA env: `<env_name>-machines` for machine capabilities and protocols, and `<env_name>-workflows` for experiment workflows.

## Steps

1. Run `puda env current` to get the active env name.

2. The env name maps to two skills:

   - `<env_name>-machines` — machines, capabilities, protocol generation
   - `<env_name>-workflows` — experiment workflows and which experiment to run

   Known envs: `bears`, `imre`, `ntu`

3. Read and follow the skills that match the task:

   | Env   | Machines skill   | Workflows skill     |
   | ----- | ---------------- | ------------------- |
   | bears | `bears-machines` | `bears-workflows`   |
   | imre  | `imre-machines`  | `imre-workflows`    |
   | ntu   | `ntu-machines`   | `ntu-workflows`     |

4. If the required skill is not installed, stop and tell the user:

   > The `<env_name>-machines` or `<env_name>-workflows` skill is not installed. Install it using `puda skills install pudap/<env_name>-skills` before continuing.

5. If the active env does not have the machines needed for the task, tell the user:

   > The current env (`<env_name>`) may not have the machines required for this task. You might need to switch envs before continuing.
