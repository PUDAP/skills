# PUDA CLI, project, and skills SOP

1. Verify `puda version` and compare with the required edge library/protocol version.
2. Install from an official release and verify a published checksum when available.
3. Log in with the explicitly supplied PUDA username; GitHub identity is separate.
4. Inspect and set NATS URLs with `puda config get nats_servers` and `puda config set nats_servers ...`.
5. Install/update skills using documented PUDA commands.
6. Initialize or locate a project containing `project.md`, `puda.config`, `puda.db`, and `protocols/`.
7. Run project-dependent protocol commands from the project root.
8. Before authoring, use `puda machine list`, `puda machine state`, and `puda machine commands <id>`.

Machine discovery can be stale. Record returned timestamps and compare with current UTC.
