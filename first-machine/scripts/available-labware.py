#!/usr/bin/env python3
"""
Available Labware Resource

Resource that exposes available labware types for the First machine.
"""

import json
import asyncio
from puda_drivers import labware


async def get_available_labware_resource() -> str:
    """Returns a JSON array of available labware names.
    
    Provides a list of all labware types that are available for use
    with the First machine.
    
    Returns:
        str: JSON-formatted array of labware names.
    """
    labware_list = labware.get_available_labware()
    return json.dumps(labware_list, indent=2)


async def main():
    """Main entry point for the script."""
    result = await get_available_labware_resource()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
