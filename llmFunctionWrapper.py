import inspect

class FunctionRegistry:
    _registry = {}

    @classmethod
    def register_function(cls, name, function):
        cls._registry[name] = function

    @classmethod
    def get_registry(cls):
        return cls._registry

    @classmethod
    def call_function(cls, name, **kwargs):
        if name in cls._registry:
            func = cls._registry[name]
            sig = inspect.signature(func)
            bound_args = sig.bind(**kwargs)
            bound_args.apply_defaults()

            return func(*bound_args.args, **bound_args.kwargs)
        else:
            raise ValueError(f"Function {name} not registered")


class ToolWrapper:
    def __init__(self, purpose, required=None, function_ref=None, **kwargs):

        if function_ref is None:
            raise ValueError("(function_ref) must be provided")
        if not callable(function_ref):
            raise TypeError("(function_ref) must be callable")

        self.name = function_ref.__name__
        self.purpose = purpose.strip()
        self.parameters = {}
        self.required = required or []
        self.function_ref = function_ref

        for param_name, param_info in kwargs.items():
            if param_name.endswith('_description'):
                continue  # Skip if this is meant to be a description.
            self._add_parameter(param_name, param_info)

        # After initializing parameters, update them with descriptions if provided
        for param_name, param_description in kwargs.items():
            if param_name.endswith('_description'):
                true_param_name = param_name.replace('_description', '')
                if true_param_name in self.parameters:
                    self.parameters[true_param_name]['description'] = param_description

        if function_ref:
            FunctionRegistry.register_function(self.name, function_ref)  # Register the function using its name

    def _add_parameter(self, name, param_info):

        # Map Python types to JSON schema types.
        type_mapping = {
            int: 'integer',
            float: 'number',
            str: 'string',
            bool: 'boolean',
            list: "array",
            tuple: "array",
            dict: "object",
            None: "null",
        }

        # Check if param_info is a list, meaning it defines an enum.
        if isinstance(param_info, list):
            parameter_type = 'array'
            enum_values = param_info
        else:
            parameter_type = type_mapping.get(param_info, 'string')
            enum_values = None

        parameter = {
            'name': name,
            'type': parameter_type,
            'enum': enum_values if enum_values else None
        }
        # Add the parameter only if it isn't an enum or it is an enum and not empty.
        if not enum_values or (enum_values and len(enum_values) > 0):
            self.parameters[name] = parameter

    def to_dict(self):
        properties = {}
        required_fields = []

        # Convert the parameters to a property list.
        for param_name, param_info in self.parameters.items():
            props = {'type': param_info['type']}
            if param_info.get('enum'):
                props['enum'] = param_info['enum']
            if param_info.get('description'):
                props['description'] = param_info['description']
            if param_name in self.required:
                required_fields.append(param_name)

            properties[param_name] = props

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
