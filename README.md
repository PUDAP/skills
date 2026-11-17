# PUDA skills (moved)

> **This repository is archived.** The PUDA agent skills now live in [PUDAP/puda](https://github.com/PUDAP/puda/tree/main/skills) under `skills/`.

Skills are now tagged with each PUDA CLI release, so the installed skills always match the CLI version they describe.

## Install or update

```sh
puda skills update
```

With no arguments, `puda skills install` / `update` install the skills from your installed CLI's release tag (for example `PUDAP/puda/tree/v0.1.6-rc2/skills`). Run `puda skills update` after every `puda update`.

Same-name skills installed from this repository are replaced. Skills that only existed here, such as `puda-memory`, are not removed automatically; run notes are now handled by `puda protocol note` (see the `puda-protocol` skill).

See [docs/skills-migration.md](https://github.com/PUDAP/puda/blob/main/docs/skills-migration.md) for details.
