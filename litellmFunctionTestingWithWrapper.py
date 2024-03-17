import litellm
import json
import os
from rich import print
from tools_wrapper import ToolWrapper, FunctionRegistry


"""
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
                            "time": {
                                "type": "string",
                                "description": "The current time in the location",
                            },
                            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                        },
                        "required": ["location"],
                    },
                },
            }
        ]
"""

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY') # litellm reads OPENAI_API_KEY from .env and sends the request

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
    name="get_current_weather",
    purpose="Get the current weather in a given location.",
    location=str,
    location_description="The city and state, e.g. San Francisco, CA",
    unit=["celsius", "fahrenheit"],  # Note that this is a list, so _add_parameter knows it's an enum
    unit_description="The unit of temperature, e.g. celsius or fahrenheit",
    required=["location"],
    function_ref= get_current_weather  # Associate the real function with this wrapper
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
    name="get_current_time",
    purpose="Get the current time in a given location.",
    location=str,
    location_description="The city and state, e.g. San Francisco, CA",
    required=["location"],
    function_ref= get_current_time  # Associate the real function with this wrapper
)



def test_parallel_function_call():
    try:

        tools = [weatherFunction, timeFunction]
        serialized_tools = [tool.to_dict() for tool in tools]

        print(FunctionRegistry.get_registry())

        # Step 1: send the conversation and available functions to the model
        messages = [{"role": "user", "content": "What's the weather and time in San Francisco? Also, please provide me the time in New York."}]
        # messages = [{"role": "user", "content": "What's the time in San Francisco, Tokyo, and Paris?"}]

        # model = "litellm/mistral/Mistral-large-cyzlm"
        # model = "gpt-3.5-turbo-1106"
        # model = "claude-3-sonnet-20240229"
        # model = "claude-3-opus-20240229"


        response = litellm.completion(
            model = "mistral/Mistral-large-cyzlm",
            messages=messages,
            tools=serialized_tools,
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
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = FunctionRegistry.call_function(
                    function_name,
                    **function_args
                )
                print("This is the function_response:\n\n", function_response)
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