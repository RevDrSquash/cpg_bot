import os
import sys
import traceback
import json
from typing import Any, Dict, Optional
from dataclasses import asdict

import pandas as pd
from difflib import SequenceMatcher

from botbuilder.core import MemoryStorage, TurnContext
from teams import Application, ApplicationOptions, TeamsAdapter
from teams.ai import AIOptions
from teams.ai.planners import AssistantsPlanner, OpenAIAssistantsOptions
from teams.state import TurnState
from teams.feedback_loop_data import FeedbackLoopData

from config import Config

config = Config()

planner = AssistantsPlanner[TurnState](
    OpenAIAssistantsOptions(api_key=config.OPENAI_API_KEY, assistant_id=config.OPENAI_ASSISTANT_ID)
)

# Define storage and application
storage = MemoryStorage()
bot_app = Application[TurnState](
    ApplicationOptions(
        bot_app_id=config.APP_ID,
        storage=storage,
        adapter=TeamsAdapter(config),
        ai=AIOptions(planner=planner, enable_feedback_loop=True),
    )
)

def filter_dataframe_by_similarity(df, column, target_strings, threshold=0.8):
    """
    Filters a Pandas DataFrame by checking the similarity of a column's values to a list of target strings.

    Args:
        df (pd.DataFrame): The DataFrame to filter.
        column (str): The name of the column to compare.
        target_strings (list): A list of target strings to compare against.
        threshold (float): The similarity ratio threshold (0 to 1).

    Returns:
        pd.DataFrame: A filtered DataFrame containing only rows with similarity above the threshold
                      for at least one target string.
    """
    def is_similar_to_any(value, targets, threshold):
        """
        Checks if the value is similar to any of the target strings.

        Args:
            value (str): The value to compare.
            targets (list): The list of target strings.
            threshold (float): The similarity ratio threshold.

        Returns:
            bool: True if the value is similar to at least one target string, False otherwise.
        """
        for target in targets:
            if SequenceMatcher(None, value, target).ratio() >= threshold:
                return True
        return False

    # Apply the similarity check and filter rows
    filtered_df = df[df[column].apply(lambda x: is_similar_to_any(x, target_strings, threshold))]

    return filtered_df

def read_project_data():
    return pd.read_csv("E:\\dev\\cpg_bot\\cpg_bot\\data\\projects.csv", dtype={'Project Name': str, 'Project Name': str, 'Year': str, 'Files': str}, keep_default_na=False)

@bot_app.ai.action("get_projects_by_year")
async def get_projects_by_year(context: TurnContext, state: TurnState):
    project_list = read_project_data()
    year = context.data.get("year")

    return project_list[ project_list['Year'] == year ][[ 'Project Name', 'Project ID', 'Year' ]].to_json(index=False, orient="records")

@bot_app.ai.action("get_project_ids")
async def get_project_ids(context: TurnContext, state: TurnState):
    project_list = read_project_data()
    project_names = context.data.get("project_names")

    project_list = filter_dataframe_by_similarity( project_list, 'Project Name', project_names )

    return project_list[[ 'Project Name', 'Project ID', 'Year' ]].to_json(index=False, orient="records")

@bot_app.ai.action("get_project_files")
async def get_project_files(context: TurnContext, state: TurnState):
    project_list = read_project_data()
    project_names = context.data.get("project_names")

    project_list = filter_dataframe_by_similarity( project_list, 'Project Name', project_names )

    return project_list[[ 'Project Name', 'Files' ]].to_json(index=False, orient="records")

@bot_app.error
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")

@bot_app.feedback_loop()
async def feedback_loop(_context: TurnContext, _state: TurnState, feedback_loop_data: FeedbackLoopData):
    # Add custom feedback process logic here.
    print(f"Your feedback is:\n{json.dumps(asdict(feedback_loop_data), indent=4)}")