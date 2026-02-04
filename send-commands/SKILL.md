---
name: send-commands
description: Send a sequence of commands to machines via NATS using CommandService. Loads commands from a JSON file and sends them sequentially, stopping on first error.
---

# Batch Commands Skill

To send a sequence of commands to a machine via NATS, use this skill to load commands from a JSON file and execute them sequentially using the CommandService.

## Required Information

Before sending batch commands, ensure a `.env` file exists in the project root with the following variables:

**Important**: You must create and configure the `.env` file first before running the script. If the `.env` file is missing or any of these variables are not set, the script will display an error message and exit.

1. **USER_ID**: Unique identifier for the user (UUID string)
2. **USERNAME**: Username of the person initiating the commands
3. **NATS_SERVERS**: Comma-separated list of NATS server URLs (e.g., "nats://host1:4222,nats://host2:4222")

Example `.env` file:
```
USER_ID=
USERNAME=
NATS_SERVERS=nats://100.86.162.126:4222,nats://100.86.162.126:4223,nats://100.86.162.126:4224
```

Additionally, the following information is required at runtime:

4. **commands_file**: Path to a JSON file containing an array of command objects
5. **machine_id**: Machine ID to send commands to (must be explicitly provided, do not default to "first")

## Execution Process

When executing batch commands, directly run the `send_batch_commands.py` script with the required parameters:

1. Ensure a `.env` file exists with `USER_ID`, `USERNAME`, and `NATS_SERVERS` variables (see Required Information above)

2. Execute the script at `scripts/send_batch_commands.py` with the following arguments:
   - `--commands-file`: Path to the JSON commands file (required)
   - `--machine-id`: Machine ID (defaults to "first" if not provided)
   - `--timeout`: Optional timeout per command in seconds (defaults to 120)
   - `--user-id`: Optional override for USER_ID from .env
   - `--username`: Optional override for USERNAME from .env
   - `--nats-servers`: Optional override for NATS_SERVERS from .env

2. The script will:
   - Load and validate the commands from the JSON file
   - Convert each command dictionary to a CommandRequest object
   - Generate a unique run_id (UUID) for this execution
   - Connect to NATS using the provided servers
   - Use CommandService's async context manager for automatic connection management
   - Call `send_queue_commands()` with all the required parameters
   - Handle the response and return appropriate exit codes

3. Check the script's exit code:
   - Exit code 0: All commands completed successfully
   - Exit code 1: Commands failed, timed out, or encountered an error

## Implementation

**Execute the script directly** at `scripts/send_batch_commands.py`. Do not reimplement the logic - use the script as-is.

The script handles:
- Loading commands from JSON
- Validating command format using CommandRequest
- Creating CommandService with async context manager
- Sending batch commands with proper error handling
- Logging command execution status
- Returning appropriate exit codes for success/failure

## Error Handling

The `send_queue_commands()` method automatically:
- Sends a START command before the sequence
- Sends commands sequentially, waiting for each response
- Stops immediately on first error or timeout
- Sends a COMPLETE command after successful completion

If any command fails, the method returns the error response immediately. Check the response status to determine success or failure.

## Notes

- Execute the script directly - it handles all the implementation details internally
- The script uses the async context manager (`async with CommandService(...)`) for automatic connection cleanup
- The script generates a unique run_id (UUID) for each execution
- Commands are sent sequentially - each command waits for the previous one to complete
- Timeout defaults to 120 seconds per command (configurable via `--timeout` argument)
- The service automatically handles signal handlers for graceful shutdown

