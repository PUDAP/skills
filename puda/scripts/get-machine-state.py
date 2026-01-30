#!/usr/bin/env python3
"""
Get Machine State Script

Script to retrieve machine state from NATS Key-Value store.

Usage:
    python get-state.py --machine-id MACHINE_ID [--nats-servers SERVERS]
"""

import json
import asyncio
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import nats
from nats.js.errors import NotFoundError


def parse_nats_servers(servers_str: str) -> list[str]:
    """Parse comma-separated NATS server URLs into a list."""
    return [s.strip() for s in servers_str.split(",")]


def load_env_config():
    """Load configuration from .env file and validate required variables."""
    # Try to load .env file from current directory or script directory
    env_path = Path(".env")
    if not env_path.exists():
        env_path = Path(__file__).parent.parent.parent / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}", file=sys.stderr)
    else:
        print("Warning: No .env file found. Using environment variables or command line arguments.", file=sys.stderr)
    
    # Load environment variables
    nats_servers_str = os.getenv("NATS_SERVERS")
    
    return nats_servers_str


async def get_machine_state(machine_id: str, nats_servers: list[str]) -> dict:
    """Get the current state of the machine from NATS Key-Value store.
    
    Args:
        machine_id: Machine ID to retrieve state for
        nats_servers: List of NATS server URLs
        
    Returns:
        dict: Machine state information or error information
    """
    
    # Derive KV bucket name from machine_id
    kv_bucket_name = f"MACHINE_STATE_{machine_id.replace('.', '-')}"
    
    nats_client = None
    try:
        # Connect to NATS
        print(f"Connecting to NATS servers: {nats_servers}", file=sys.stderr)
        nats_client = await nats.connect(
            servers=nats_servers,
            connect_timeout=10,
            reconnect_time_wait=2,
            max_reconnect_attempts=-1,
        )
        
        # Initialize JetStream and Key-Value store
        nats_js = nats_client.jetstream()
        kv = await nats_js.key_value(kv_bucket_name)
        print(f"Connected to NATS and KV bucket: {kv_bucket_name}", file=sys.stderr)
        
        # Get the machine state
        print(f"Retrieving state for machine: {machine_id}", file=sys.stderr)
        entry = await kv.get(machine_id)
        
        if entry:
            status = json.loads(entry.value.decode())
            return status
        else:
            return {"error": f"Could not find state for {machine_id}"}
        
    except NotFoundError as e:
        return {"error": f"KV bucket or key not found for {machine_id}: {e}"}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse state JSON for {machine_id}: {e}"}
    except (KeyError, AttributeError) as e:
        return {"error": f"Invalid state data format for {machine_id}: {e}"}
    except RuntimeError as e:
        return {"error": f"NATS connection error: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error retrieving state for {machine_id}: {e}"}
    finally:
        # Close NATS connection
        if nats_client is not None:
            await nats_client.close()


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Get machine state from NATS Key-Value store",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # With .env file configured
  python get-state.py --machine-id first
  
  # Full command line (overrides .env values)
  python get-state.py --machine-id first --nats-servers "nats://host1:4222,nats://host2:4222"
        """
    )
    
    parser.add_argument(
        "--machine-id",
        type=str,
        required=True,
        help="Machine ID to retrieve state for"
    )
    
    parser.add_argument(
        "--nats-servers",
        type=str,
        help="Comma-separated NATS server URLs (overrides NATS_SERVERS from .env)"
    )
    
    args = parser.parse_args()
    
    # Load from .env file (unless overridden by command line)
    env_nats_servers = load_env_config()
    
    nats_servers_str = args.nats_servers or env_nats_servers
    
    # Validate required parameters
    if not nats_servers_str:
        print("Error: NATS_SERVERS must be provided via .env file or --nats-servers argument", file=sys.stderr)
        print("Example .env file:", file=sys.stderr)
        print("  NATS_SERVERS=nats://host1:4222,nats://host2:4222", file=sys.stderr)
        return 1
    
    # Parse NATS servers
    nats_servers = parse_nats_servers(nats_servers_str)
    
    # Get machine state
    result = asyncio.run(get_machine_state(machine_id=args.machine_id, nats_servers=nats_servers))
    
    # Print result as JSON
    print(json.dumps(result, indent=2))
    
    # Return error code if there was an error
    return 1 if "error" in result else 0


if __name__ == "__main__":
    exit(main())

