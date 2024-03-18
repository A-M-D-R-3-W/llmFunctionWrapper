# llmFunctionWrapper

A Python module designed to simplify the process of creating and managing function calls to OpenAI's API, as well as models using LiteLLM's framework.


## Quickstart

### 1. Defining Functions

First, define your functions following standard Python syntax, in the same way OpenAI and LiteLLM expect. For example:

```python
def an_awesome_function(variable1, variable2="A default value for variable2"):
    # Function body ...
    return desiredVariable
```

### 2. Wrapping your Functions

Use the `ToolWrapper` class to create your function descriptions which will be passed to the LLM. Add relevant details such as purpose, parameters, and descriptions.

The description will look like this:
```python
awesomeFunction = ToolWrapper(
    function_ref=an_awesome_function,
    purpose="An awesome function that does something amazing.",
    variable1=int,
    variable1_description="The first variable that will be used to do the first awesome thing.",
    variable2=["option1", "option2"],
    variable2_description="The second variable that will be used to do the second awesome thing.",
    required=["variable1", "variable2"]
)
```

### 3. Submitting Your Functions to the API

Before you make your API request, you must serialize your function descriptions in OpenAI and LiteLLM's tool format.
```python
unserializedTools = [awesomeFunction]
tools = [tool.to_dict() for tool in unserializedTools]
```
Alternatively, you can serialize each function individually in-line:
```python
tools = [awesomeFunction.to_dict(), otherFunction.to_dict()]
)
```

## Examples

### Simple Single Function Call
A simple function calling example from LiteLLM docs:

```python
import litellm
import json
import os

# set openai api key
os.environ['OPENAI_API_KEY'] = "" # litellm reads OPENAI_API_KEY from .env and sends the request
# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": "celsius"})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": "celsius"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

messages = [{"role": "user", "content": "What's the weather like in San Francisco, Tokyo, and Paris?"}]
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

response = litellm.completion(
    model="gpt-3.5-turbo-1106",
    messages=messages,
    tools=tools,
    tool_choice="auto",  # auto is default, but we'll be explicit
)
print("\nLLM Response1:\n", response)
response_message = response.choices[0].message
tool_calls = response.choices[0].message.tool_calls
```


Modified for use with llmFunctionWrapper:

```python
import litellm
import json
import os
from llmFunctionWrapper import ToolWrapper

# set openai api key
os.environ['OPENAI_API_KEY'] = "" # litellm reads OPENAI_API_KEY from .env and sends the request
# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": "celsius"})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": "celsius"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

weatherFunction = ToolWrapper(
    function_ref=get_current_weather,
    purpose="Get the current weather in a given location.",
    location=str,
    location_description="The city and state, e.g. San Francisco, CA",
    unit=["celsius", "fahrenheit"],
    unit_description="The unit of temperature, e.g. celsius or fahrenheit",
    required=["location"],
)

messages = [{"role": "user", "content": "What's the weather like in San Francisco, Tokyo, and Paris?"}]

unserializedTools = [weatherFunction]
tools = [tool.to_dict() for tool in unserializedTools]

response = litellm.completion(
    model="gpt-3.5-turbo-1106",
    messages=messages,
    tools=tools,
    tool_choice="auto",  # auto is default, but we'll be explicit
)
print("\nLLM Response1:\n", response)
response_message = response.choices[0].message
tool_calls = response.choices[0].message.tool_calls
```


Note that

```python
weatherFunction = ToolWrapper(
    function_ref=get_current_weather,
    purpose="Get the current weather in a given location.",
    location=str,
    location_description="The city and state, e.g. San Francisco, CA",
    unit=["celsius", "fahrenheit"],
    unit_description="The unit of temperature, e.g. celsius or fahrenheit",
    required=["location"],
)

unserializedTools = [weatherFunction]
tools = [tool.to_dict() for tool in unserializedTools]
```

Is a direct replacement for, and is identical to

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]
```

### Using Multiple Functions

Let's say we want two functions - one to get the weather (from the example above), and one to get the time.

```python
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": "celsius"})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": "celsius"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

weatherFunction = ToolWrapper(
    function_ref=get_current_weather,
    purpose="Get the current weather in a given location.",
    location=str,
    location_description="The city and state, e.g. San Francisco, CA",
    unit=["celsius", "fahrenheit"],
    unit_description="The unit of temperature, e.g. celsius or fahrenheit",
    required=["location"],
)

def get_current_time(location):
    """Get the current time in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": location, "time": "3:00 PM"})
    elif "san francisco" in location.lower():
        return json.dumps({"location": location, "time": "12:00 PM"})
    elif "paris" in location.lower():
        return json.dumps({"location": location, "time": "9:00 PM"})
    else:
        return "I don't know the time in " + location

timeFunction = ToolWrapper(
    function_ref= get_current_time,
    purpose="Get the current time in a given location.",
    location=str,
    location_description="The city and state, e.g. San Francisco, CA",
    required=["location"],
)

unserializedTools = [weatherFunction, timeFunction]
tools = [tool.to_dict() for tool in unserializedTools]
```
Notice that the only difference compared to calling a single function is adding **timeFunction** to the **unserializedTools** array.

```python
unserializedTools = [weatherFunction, timeFunction]
tools = [tool.to_dict() for tool in unserializedTools]
```


### Parallel Function Call

Expanding upon the example given above, we can utilize parallel function calling with various optimizations as well. The following example was pulled from LiteLLM docs:

```python
import litellm
import json
import os

# set openai api key
os.environ['OPENAI_API_KEY'] = "" # litellm reads OPENAI_API_KEY from .env and sends the request

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": "celsius"})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": "celsius"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})


def test_parallel_function_call():
    try:
        # Step 1: send the conversation and available functions to the model
        messages = [{"role": "user", "content": "What's the weather like in San Francisco, Tokyo, and Paris?"}]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get the current weather in a given location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA",
                            },
                            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                        },
                        "required": ["location"],
                    },
                },
            }
        ]
        response = litellm.completion(
            model="gpt-3.5-turbo-1106",
            messages=messages,
            tools=tools,
            tool_choice="auto",  # auto is default, but we'll be explicit
        )
        print("\nFirst LLM Response:\n", response)
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        print("\nLength of tool calls", len(tool_calls))

        # Step 2: check if the model wanted to call a function
        if tool_calls:
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = {
                "get_current_weather": get_current_weather,
            }  # only one function in this example, but you can have multiple
            messages.append(response_message)  # extend conversation with assistant's reply

            # Step 4: send the info for each function call and function response to the model
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(
                    location=function_args.get("location"),
                    unit=function_args.get("unit"),
                )
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )  # extend conversation with function response
            second_response = litellm.completion(
                model="gpt-3.5-turbo-1106",
                messages=messages,
            )  # get a new response from the model where it can see the function response
            print("\nSecond LLM response:\n", second_response)
            return second_response
    except Exception as e:
      print(f"Error occurred: {e}")

test_parallel_function_call()
```

Modified for use with llmFunctionWrapper:
```python
import litellm
import json
import os
from llmFunctionWrapper import ToolWrapper, FunctionRegistry

# set openai api key
os.environ['OPENAI_API_KEY'] = "" # litellm reads OPENAI_API_KEY from .env and sends the request

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": "celsius"})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": "celsius"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

weatherFunction = ToolWrapper(
    function_ref=get_current_weather,
    purpose="Get the current weather in a given location.",
    location=str,
    location_description="The city and state, e.g. San Francisco, CA",
    unit=["celsius", "fahrenheit"],
    unit_description="The unit of temperature, e.g. celsius or fahrenheit",
    required=["location"],
)

def test_parallel_function_call():
    try:
        # Step 1: send the conversation and available functions to the model
        messages = [{"role": "user", "content": "What's the weather like in San Francisco, Tokyo, and Paris?"}]

        unserializedTools = [weatherFunction]
        tools = [tool.to_dict() for tool in unserializedTools]

        response = litellm.completion(
            model="gpt-3.5-turbo-1106",
            messages=messages,
            tools=tools,
            tool_choice="auto",  # auto is default, but we'll be explicit
        )
        print("\nFirst LLM Response:\n", response)
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        print("\nLength of tool calls", len(tool_calls))

        # Step 2: check if the model wanted to call a function
        if tool_calls:
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = FunctionRegistry.get_registry()
            messages.append(response_message)  # extend conversation with assistant's reply

            # Step 4: send the info for each function call and function response to the model
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                function_response = FunctionRegistry.call_function(
                    function_name,
                    **function_args
                )
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )  # extend conversation with function response
            second_response = litellm.completion(
                model="gpt-3.5-turbo-1106",
                messages=messages,
            )  # get a new response from the model where it can see the function response
            print("\nSecond LLM response:\n", second_response)
            return second_response
    except Exception as e:
      print(f"Error occurred: {e}")

test_parallel_function_call()
```
There are a few changes that have occured.

1. The function was defined using ToolWrapper(), exactly as was explained in the **Simple Single Function Call** example provided.
2. The method for passing functions to call has changed as shown below:

The original implementation
```python
# Step 2: check if the model wanted to call a function
        if tool_calls:
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = {
                "get_current_weather": get_current_weather,
            }  # only one function in this example, but you can have multiple
            messages.append(response_message)  # extend conversation with assistant's reply

            # Step 4: send the info for each function call and function response to the model
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(
                    location=function_args.get("location"),
                    unit=function_args.get("unit"),
                )
```
Has became

```python
# Step 2: check if the model wanted to call a function
        if tool_calls:
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            messages.append(response_message)  # extend conversation with assistant's reply

            # Step 4: send the info for each function call and function response to the model
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                function_response = FunctionRegistry.call_function(
                    function_name,
                    **function_args
                )
```

With this setup, there is no longer a need to specify individual functions/arguments to call, the entire process is automated.



```python

```
