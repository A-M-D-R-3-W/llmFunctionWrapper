'''
llmFunctionWrapper
by A-M-D-R-3-W on GitHub

A Python module designed to simplify the process of creating and managing
function calls to OpenAI's API, as well as models using LiteLLM's API framework.
'''

import inspect

# A registry for holding references to functions by name.
class FunctionRegistry:
    _registry = {}  # Class-level dictionary to hold function references.

    # Registers a function by name in the registry.
    @classmethod
    def register_function(cls, name, function):
        cls._registry[name] = function

    # Returns the current state of the registry.
    @classmethod
    def get_registry(cls):
        return cls._registry

    # Calls a registered function by name with arguments.
    @classmethod
    def call_function(cls, name, **kwargs):
        if name in cls._registry:  # Check if function is registered.
            func = cls._registry[name]
            sig = inspect.signature(func)  # Get function signature.
            bound_args = sig.bind(**kwargs)  # Bind given arguments.
            bound_args.apply_defaults()  # Apply defaults for missing args.

            return func(*bound_args.args, **bound_args.kwargs)
        else:
            raise ValueError(f"Function {name} not registered")

# Class for wrapping functions with additional metadata and registering them.
class ToolWrapper:
    def __init__(self, purpose, required=None, function_ref=None, **kwargs):
        if function_ref is None:
            raise ValueError("'function_ref' must be provided")
        if not callable(function_ref):
            raise TypeError("'function_ref)' must be callable")

        self.name = function_ref.__name__  # Function name.
        self.purpose = purpose.strip()  # Purpose/description of the function.
        self.parameters = {}  # Dictionary to hold parameter info.
        self.required = required or []  # List of required parameter names.
        self.function_ref = function_ref  # Reference to the actual function.

        # Create a set of parameter names for which descriptions are expected to be provided
        description_keys = {key.replace('_description', '') for key in kwargs if key.endswith('_description')}
        param_keys = {key for key in kwargs if not key.endswith('_description')}

        # Check for descriptions provided without the corresponding parameter
        for desc_key in description_keys:
            if desc_key not in param_keys:
                raise ValueError(f"Description provided for '{desc_key}', but '{desc_key}' parameter is not present")

        # Check for each parameter having a corresponding description
        for param_name in param_keys:
            if param_name not in description_keys:
                raise ValueError(f"Description for '{param_name}' not provided")
            # Add parameter information using the _add_parameter method
            self._add_parameter(param_name, kwargs[param_name])

        # Add parameter descriptions if provided.
        for param_name, param_description in kwargs.items():
            if param_name.endswith('_description'):
                true_param_name = param_name.replace('_description', '')
                if true_param_name in self.parameters:
                    self.parameters[true_param_name]['description'] = param_description

        # Register the function in the global registry.
        FunctionRegistry.register_function(self.name, function_ref)

    # Adds parameter information to the parameters dictionary.
    def _add_parameter(self, name, param_info):
        type_mapping = {  # Map Python types to JSON schema types.
            int: 'integer',
            float: 'number',
            str: 'string',
            bool: 'boolean',
            list: "array",
            tuple: "array",
            dict: "object",
            None: "null",
        }

        if isinstance(param_info, list):  # Check if this is an enum parameter.
            parameter_type = 'array'
            enum_values = param_info
        else:  # Otherwise, use the type mapping.
            parameter_type = type_mapping.get(param_info, 'string')
            enum_values = None

        # Construct the parameter dictionary.
        parameter = {
            'name': name,
            'type': parameter_type,
            'enum': enum_values if enum_values else None
        }

        # Only add the parameter if it's not an empty enum.
        if not enum_values or (enum_values and len(enum_values) > 0):
            self.parameters[name] = parameter

    # Converts the tool wrapper metadata into a standardized dictionary format.
    def to_dict(self):
        properties = {}
        required_fields = []

        # Convert parameters to JSON schema properties.
        for param_name, param_info in self.parameters.items():
            props = {'type': param_info['type']}
            if param_info.get('enum'):  # Add enum values if present.
                props['enum'] = param_info['enum']
            if param_info.get('description'):  # Add description if present.
                props['description'] = param_info['description']
            if param_name in self.required:  # Mark as required if necessary.
                required_fields.append(param_name)

            properties[param_name] = props

        # Construct and return the full function metadata dictionary.
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.purpose,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required_fields
                }
            }
        }
