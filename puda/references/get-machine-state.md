---
name: get-machine-state
description: Retrieve machine state from NATS Key-Value store. Connects to NATS JetStream and fetches the current state information for a specified machine.
---

# Get Machine State Skill

To retrieve the current state of a machine from the NATS Key-Value store, use this skill to connect to NATS JetStream and fetch the machine's state information.

## Required Information

Before retrieving machine state, ensure a `.env` file exists in the project root with the following variable:

**Important**: You must create and configure the `.env` file first before running the script. If the `.env` file is missing or the variable is not set, you can provide it via command line arguments.

1. **NATS_SERVERS**: Comma-separated list of NATS server URLs (e.g., "nats://host1:4222,nats://host2:4222")

Example `.env` file:
```
NATS_SERVERS=nats://100.86.162.126:4222,nats://100.86.162.126:4223,nats://100.86.162.126:4224
```

Additionally, the following information is required at runtime:

2. **machine_id**: Machine ID to retrieve state for (must be explicitly provided)

## Execution Process

When retrieving machine state, directly run the `get-machine-state.py` script with the required parameters:

1. Ensure a `.env` file exists with `NATS_SERVERS` variable (see Required Information above), or provide it via command line

2. Execute the script at `scripts/get-machine-state.py` with the following arguments:
   - `--machine-id`: Machine ID to retrieve state for (required)
   - `--nats-servers`: Optional comma-separated NATS server URLs (overrides NATS_SERVERS from .env)

3. The script will:
   - Load NATS server configuration from `.env` file or command line arguments
   - Connect to NATS servers
   - Derive the KV bucket name from the machine_id (format: `MACHINE_STATE_{machine_id}`)
   - Retrieve the machine state from the Key-Value store
   - Output the state as formatted JSON to stdout
   - Return appropriate exit codes

4. Check the script's exit code:
   - Exit code 0: State retrieved successfully
   - Exit code 1: Error occurred (connection failure, bucket not found, invalid state, etc.)

## Implementation

**Execute the script directly** at `scripts/get-machine-state.py`. Do not reimplement the logic - use the script as-is.

The script handles:
- Loading configuration from `.env` file or command line
- Connecting to NATS servers with automatic reconnection
- Accessing JetStream Key-Value store
- Retrieving and parsing machine state JSON
- Error handling for connection issues, missing buckets, and invalid data
- Automatic connection cleanup

## Output Format

The script outputs the machine state as formatted JSON to stdout. The output will either be:
- A JSON object containing the machine state information
- A JSON object with an `error` field if something went wrong

## Error Handling

The script handles various error conditions:
- **BucketNotFoundError**: KV bucket or key not found for the specified machine_id

All errors are returned as JSON objects with an `error` field, and the script exits with code 1.

## Notes

- Execute the script directly - it handles all the implementation details internally
- The script automatically derives the KV bucket name from the machine_id (replacing dots with hyphens)
- The script uses async/await for NATS operations
- Connection is automatically closed after retrieval
- The script searches for `.env` file in the current directory or script's parent directory
- Command line arguments override `.env` file values
- All diagnostic messages are printed to stderr, while the JSON result is printed to stdout