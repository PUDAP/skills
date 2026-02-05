#!/usr/bin/env python3
"""
Available Commands Resource

Resource that exposes available Biologic commands and their parameters.
"""

import json
import inspect
import typing
import sys

try:
    from puda_drivers.machines import Biologic
except ImportError:
    print(json.dumps({
        "error": "Could not import Biologic",
        "message": "Please ensure puda_drivers is installed and Biologic is accessible from puda_drivers.machines"
    }, indent=2))
    sys.exit(1)


def _get_type_name(annotation) -> str:
    """Extract a clean type name from a type annotation."""
    if annotation == inspect.Parameter.empty:
        return "Any"
    
    # Handle typing constructs (Optional, Union, List, etc.)
    if hasattr(typing, 'get_origin') and typing.get_origin(annotation):
        origin = typing.get_origin(annotation)
        args = typing.get_args(annotation)
        
        # Handle Optional[T] -> "Optional[T]" or just the inner type if it's Optional[None, T]
        if origin is typing.Union:
            # Filter out NoneType for Optional
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                return _get_type_name(non_none_args[0])
            return f"Union[{', '.join(_get_type_name(arg) for arg in args)}]"
        
        # Handle List[T], Dict[K, V], etc.
        if args:
            args_str = ', '.join(_get_type_name(arg) for arg in args)
            origin_name = origin.__name__ if hasattr(origin, '__name__') else str(origin)
            return f"{origin_name}[{args_str}]"
        return origin.__name__ if hasattr(origin, '__name__') else str(origin)
    
    # Handle built-in types and classes
    if hasattr(annotation, '__name__'):
        return annotation.__name__
    
    # Fallback to string representation, but clean it up
    type_str = str(annotation)
    if type_str.startswith("<class '") and type_str.endswith("'>"):
        return type_str[9:-2]  # Extract "str" from "<class 'str'>"
    
    return type_str


def get_available_commands_resource() -> str:
    """Returns a JSON string describing all available Biologic commands and their parameters.
    
    Provides comprehensive documentation of all commands available for the Biologic,
    including parameter types, descriptions, and example usage.
    
    Returns:
        str: JSON-formatted object containing command documentation.
    """
    commands = []
    
    # Get all public instance methods from the Biologic class (excluding private methods starting with _)
    # In Python 3, class methods are functions, not methods, so we use isfunction
    for name, method in inspect.getmembers(Biologic, predicate=inspect.isfunction):
        if not name.startswith('_'):
            # Get method signature
            sig = inspect.signature(method)
            
            # Extract parameters (skip 'self')
            params = {}
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                    
                param_type_str = _get_type_name(param.annotation)
                param_default = param.default if param.default != inspect.Parameter.empty else None
                param_required = param.default == inspect.Parameter.empty
                
                param_info = {
                    "name": param_name,
                    "type": param_type_str,
                    "default": str(param_default) if param_default is not None else None,
                    "required": param_required
                }
                params[param_name] = param_info
            
            # Get docstring
            docstring = inspect.getdoc(method) or ""
            
            command_info = {
                "command": name,
                "docstring": docstring,
                "parameters": params,
            }
            commands.append(command_info)
    
    return json.dumps(commands, indent=2)


def main():
    """Main entry point for the script."""
    try:
        result = get_available_commands_resource()
        print(result)
    except (ImportError, AttributeError, TypeError) as e:
        error_msg = {
            "error": f"Failed to generate command documentation: {str(e)}",
            "message": "Please ensure easy_biologic is installed and Biologic is accessible."
        }
        print(json.dumps(error_msg, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()

