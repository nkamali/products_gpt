import json
import asyncio
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError


client = AsyncOpenAI()

# Define a timeout duration in seconds
TIMEOUT_DURATION = 120  # For example, 10 seconds


async def get_completion_from_messages(
        messages,
        model="gpt-3.5-turbo",
        temperature=0,
        max_tokens=1000):
    chat_completion_response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return chat_completion_response.choices[0].message.content


async def get_moderation_from_input(moderation_input):
    try:
        print("in get_moderation_from_input. moderation_input: ", moderation_input)
        response = await asyncio.wait_for(client.moderations.create(input=moderation_input), TIMEOUT_DURATION)
        return response
    except asyncio.TimeoutError:
        # Handle a timeout situation
        print("The request to OpenAI timed out.")
        return None
    except APIConnectionError as e:
        # Handle connection error here
        print(f"Failed to connect to OpenAI API: {e}")
        pass
    except APIError as e:
        # Handle API error here, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")
        pass
    except RateLimitError as e:
        # Handle rate limit error (we recommend using exponential backoff)
        print(f"OpenAI API request exceeded rate limit: {e}")
        pass
    except Exception as e:
        # Handle other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return None

def read_string_to_list(input_string):
    if input_string is None:
        return None

    try:
        input_string = input_string.replace("'", "\"")  # Replace single quotes with double quotes for valid JSON
        data = json.loads(input_string)
        return data
    except json.JSONDecodeError:
        print("Error: Invalid JSON string")
        return None