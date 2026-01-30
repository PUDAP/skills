#!/usr/bin/env python3
"""
Executable script for sending batch commands to machines via NATS.

This script loads commands from a JSON file and sends them sequentially
using CommandService. It prompts for required parameters or accepts them
as command-line arguments.

Usage:
    python send_batch_commands.py [--user-id USER_ID] [--username USERNAME] 
                                  [--nats-servers SERVERS] [--commands-file FILE]
                                  [--machine-id MACHINE_ID]
"""

import json
import uuid
import asyncio
import logging
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
from puda_comms import CommandService
from puda_comms.models import CommandRequest, CommandResponseStatus, NATSMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def parse_nats_servers(servers_str: str) -> list[str]:
    """Parse comma-separated NATS server URLs into a list."""
    return [s.strip() for s in servers_str.split(",")]


def load_commands(commands_file: Path) -> list[dict]:
    """Load commands from JSON file."""
    if not commands_file.exists():
        raise FileNotFoundError(f"Commands file not found: {commands_file}")
    
    with open(commands_file, "r", encoding="utf-8") as f:
        commands = json.load(f)
    
    if not isinstance(commands, list):
        raise ValueError("Commands file must contain a JSON array")
    
    return commands


async def send_batch_commands(
    commands_file: Path,
    user_id: str,
    username: str,
    nats_servers: list[str],
    machine_id: str,
    timeout: int = 120
) -> bool:
    """
    Send batch commands from JSON file.
    
    Returns True if all commands succeeded, False otherwise.
    """
    logger.info("Starting batch command execution")
    logger.info("Commands file: %s", commands_file)
    logger.info("User: %s (%s)", username, user_id)
    logger.info("Machine: %s", machine_id)
    logger.info("NATS servers: %s", nats_servers)
    
    # Generate unique run_id for this execution
    run_id = str(uuid.uuid4())
    logger.info("Run ID: %s", run_id)
    
    try:
        # Load commands from JSON file
        command_dicts = load_commands(commands_file)
        logger.info("Loaded %d commands from file", len(command_dicts))
        
        # Convert to CommandRequest objects
        requests = []
        for i, cmd_dict in enumerate(command_dicts, 1):
            try:
                request = CommandRequest(**cmd_dict)
                requests.append(request)
            except Exception as e:
                logger.error("Failed to parse command %d: %s", i, e)
                logger.error("Command data: %s", cmd_dict)
                return False
        
        logger.info("Converted %d commands to CommandRequest objects", len(requests))
        
        # Send commands using CommandService
        async with CommandService(servers=nats_servers) as service:
            logger.info("Connected to NATS, sending batch commands...")
            
            reply: NATSMessage = await service.send_queue_commands(
                requests=requests,
                machine_id=machine_id,
                run_id=run_id,
                user_id=user_id,
                username=username,
                timeout=timeout
            )
            
            if reply is None:
                logger.error("Batch commands failed or timed out")
                return False
            
            if reply.response and reply.response.status == CommandResponseStatus.SUCCESS:
                logger.info("Batch commands completed successfully!")
                if reply.response.data:
                    logger.info("Response data: %s", reply.response.data)
                return True
            else:
                logger.error("Batch commands failed with status: %s", 
                           reply.response.status if reply.response else "UNKNOWN")
                if reply.response and reply.response.message:
                    logger.error("Error message: %s", reply.response.message)
                return False
                
    except FileNotFoundError as e:
        logger.error("File error: %s", e)
        return False
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in commands file: %s", e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during batch command execution: %s", e)
        return False


def load_env_config():
    """Load configuration from .env file and validate required variables."""
    # Try to load .env file from current directory or script directory
    env_path = Path(".env")
    if not env_path.exists():
        env_path = Path(__file__).parent.parent / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("Loaded environment variables from %s", env_path)
    else:
        logger.error("No .env file found. Please create a .env file in the project root with the following variables:")
        logger.error("  USER_ID=<your-user-id-uuid>")
        logger.error("  USERNAME=<your-username>")
        logger.error("  NATS_SERVERS=<comma-separated-nats-urls>")
        logger.error("Example .env file location: %s", env_path.absolute())
        return None, None, None
    
    # Load required environment variables
    user_id = os.getenv("USER_ID")
    username = os.getenv("USERNAME")
    nats_servers_str = os.getenv("NATS_SERVERS")
    
    # Validate all required variables are present
    missing = []
    if not user_id:
        missing.append("USER_ID")
    if not username:
        missing.append("USERNAME")
    if not nats_servers_str:
        missing.append("NATS_SERVERS")
    
    if missing:
        logger.error("Missing required environment variables in .env file:")
        for var in missing:
            logger.error("  %s", var)
        logger.error("Please add these variables to your .env file.")
        logger.error("Example .env file location: %s", env_path.absolute())
        return None, None, None
    
    return user_id, username, nats_servers_str


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Send batch commands to machines via NATS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # With .env file configured
  python send_batch_commands.py --commands-file commands.json --machine-id first
  
  # Full command line (overrides .env values)
  python send_batch_commands.py \\
    --user-id "550e8400-e29b-41d4-a716-446655440000" \\
    --username "john_doe" \\
    --nats-servers "nats://host1:4222,nats://host2:4222" \\
    --commands-file commands.json \\
    --machine-id first
        """
    )
    
    parser.add_argument(
        "--user-id",
        type=str,
        help="User ID (UUID string) - overrides USER_ID from .env"
    )
    
    parser.add_argument(
        "--username",
        type=str,
        help="Username - overrides USERNAME from .env"
    )
    
    parser.add_argument(
        "--nats-servers",
        type=str,
        help="Comma-separated NATS server URLs - overrides NATS_SERVERS from .env"
    )
    
    parser.add_argument(
        "--commands-file",
        type=Path,
        help="Path to JSON file containing array of commands"
    )
    
    parser.add_argument(
        "--machine-id",
        type=str,
        default="first",
        help="Machine ID (default: 'first')"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Timeout per command in seconds (default: 120)"
    )
    
    args = parser.parse_args()
    
    # Load from .env file (unless overridden by command line)
    env_user_id, env_username, env_nats_servers = load_env_config()
    if env_user_id is None:
        return 1
    
    # Use command line args if provided, otherwise use .env values
    user_id = args.user_id or env_user_id
    username = args.username or env_username
    nats_servers_str = args.nats_servers or env_nats_servers
    
    commands_file = args.commands_file
    if not commands_file:
        commands_file_str = input("Enter path to commands JSON file: ").strip()
        if not commands_file_str:
            logger.error("commands_file is required")
            return 1
        commands_file = Path(commands_file_str)
    
    # Parse NATS servers
    nats_servers = parse_nats_servers(nats_servers_str)
    
    # Execute batch commands
    success = asyncio.run(send_batch_commands(
        commands_file=commands_file,
        user_id=user_id,
        username=username,
        nats_servers=nats_servers,
        machine_id=args.machine_id,
        timeout=args.timeout
    ))
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

