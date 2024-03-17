
class ToolWrapper:
    def __init__(self, name, purpose, required=None, **kwargs):
        self.name = name
        self.purpose = purpose.strip()
        self.parameters = {}
        self.required = required or []

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

    def _add_parameter(self, name, param_info):

        # Map Python types to JSON schema types.
        type_mapping = {
            int: 'integer',
            float: 'number',
            str: 'string',
            bool: 'boolean'
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
