import asyncio, os, argparse
from teams.ai.planners import AssistantsPlanner
from openai.types.beta import AssistantCreateParams
from openai.types.beta.function_tool_param import FunctionToolParam
from openai.types.shared_params import FunctionDefinition

from dotenv import load_dotenv

load_dotenv(f'{os.getcwd()}/env/.env.local.user', override=True)

def load_keys_from_args():
    parser = argparse.ArgumentParser(description='Load keys from command input parameters.')
    parser.add_argument('--api-key', type=str, required=True, help='OpenAI API key for authentication')
    args = parser.parse_args()
    return args

async def main():
    args = load_keys_from_args()

    options = AssistantCreateParams(
        name="Assistant",
        instructions="\n".join([
            "You are an intelligent bot that can",
            "- write and run code to answer math questions",
            "- use the provided functions to answer questions"
        ]),
        tools=[
            {
                "type": "code_interpreter",
            },
            FunctionToolParam(
                type="function",
                function=FunctionDefinition(
                    name="getCurrentWeather",
                    description="Get the weather in location",
                    parameters={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state e.g. San Francisco, CA",
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["c", "f"],
                            },
                        },
                        "required": ["location"],
                    }
                )
            ),
            FunctionToolParam(
                type="function",
                function=FunctionDefinition(
                    name="getNickname",
                    description="Get the nickname of a city",
                    parameters={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state e.g. San Francisco, CA",
                            },
                        },
                        "required": ["location"],
                    }
                )
            )            
        ],
        model="gpt-3.5-turbo",
    )

    assistant = await AssistantsPlanner.create_assistant(api_key=args.api_key, api_version="", organization="", endpoint="", request=options)
    print(assistant.tools)
    print(f"Created a new assistant with an ID of: {assistant.id}")

asyncio.run(main())