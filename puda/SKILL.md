---
name: puda
description: Setup puda project, CLI installation, and project/experiment structure. Use when initializing a Puda project, puda experiment, or when updating skills is needed
---

## Setting up new puda project

1. **Check installation**: Determine how to invoke the CLI — use `puda` if installed globally, or from the project root use `./puda` on Unix/macOS or `.\puda.exe` on Windows if only a local binary exists. If it's missing, direct the user to the [Puda releases page](https://github.com/PUDAP/puda/releases). Use that same invocation (`puda`, `./puda`, or `.\puda.exe`) consistently in all steps below.
2. **Ensure Python/pip and puda-drivers**: Ensure `python3` and `pip` are available; install them first if missing. Then install or upgrade the `puda-drivers` package: `pip install --upgrade puda-drivers`.
3. **Login**: Log in to puda with `puda login`; you will need to enter a username.
4. **New project**: run `puda init` (e.g. `puda init .` or `puda init <folder_name>`).
5. **Install skills**: Install skills using `puda skills install`.

Only after the CLI is installed and the project is initialized, proceed with protocol generation, machine commands, or experiment workflows.

## Project folder structure

**Project root** contains `agents.md`, skills, `puda.config` and `puda.db` (created by `puda init`, `./puda init`, or `.\puda.exe init`).

**Experiments** live as **folders** under the project root. Each experiment folder is named with the experiment’s **UUID** (generated in the “New puda experiment” flow).

Inside each experiment folder:

- **experiment.md** — single source of truth (maintained by the **puda-memory** skill)
- **protocols/** — store all generated protocol files (created by **puda-protocol-gen**)
- **logs/** — store log files from runs

## New puda experiment

When starting a new experiment:

1. Generate a unique UUID for the experiment:
   ```bash
   python -c "import uuid; print(uuid.uuid4())"
   ```
2. Create an experiment folder under the project root. **Name the folder with the UUID from step 1** (e.g. `a1b2c3d4-e5f6-7890-abcd-ef1234567890`).
3. Create **experiment.md** in the experiment folder root with the UUID and the experiment objective. Use the **puda-memory** skill; if the user has not provided an objective, ask them for it before creating the file. Template:

   ```markdown
   # Experiment

   experiment_id: <uuid-from-step-1>
   objective: <objective>
   ```

## Updating puda skills

To refresh or update puda skills:

```bash
puda skills update
```
(or `./puda skills update` / `.\puda.exe skills update` if using the local CLI)
