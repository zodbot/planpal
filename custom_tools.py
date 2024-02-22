# Create tools for LLamaIndex
import os
from datetime import datetime

import pytz
from llama_index.agent import OpenAIAssistantAgent, ContextRetrieverOpenAIAgent
from llama_index import (
    ServiceContext,
    StorageContext,
    SummaryIndex,
    VectorStoreIndex, SimpleDirectoryReader,
)
from llama_index.llms import OpenAI
from llama_index.tools import QueryEngineTool, FunctionTool

from my_calendar import MyCalendar

local_timezone = datetime.now(pytz.timezone('America/New_York'))  # Replace with your time zone
current_datetime = local_timezone.strftime('%Y-%m-%d %H:%M:%S')

my_calendar = MyCalendar()

# custom tool to add to the calendar
create_event_tool = FunctionTool.from_defaults(fn=my_calendar.create_event,
                                               name="create_event",
                                               description="Add an event to my Google Calendar"
                                                           "The time of the event in ISO 8601 format, e.g., "
                                                           "'2024-01-10T09:00:00"
                                                           f"today's Date and Time: {current_datetime}, Local Time "
                                                           f"Zone: {local_timezone}"
                                                           "The user must specify time and date in the request."
                                                           "location for the event is optional. Leave it blank if it "
                                                           "is not specified."
                                               )
# custom tool to fetch events from calendar
fetch_events_tool = FunctionTool.from_defaults(fn=my_calendar.get_events,
                                               name="fetch_new_events",
                                               description="Retrieves a set number of upcoming events from Google "
                                                           "Calendar."
                                                           "This function is designed to provide the next n events ")

# custom tool to fetch events from calendar
fetch_events_tool_n_days = FunctionTool.from_defaults(fn=my_calendar.get_events_n_days,
                                                      name="fetch_new_events",
                                                      description="Retrieves events for the specified number of upcoming "
                                                                  "days from the Google Calendar. Users are required to "
                                                                  "specify the number of days for which they want to view events"
                                                                  "This function will then fetch and display events from Google Calendar for that duration.")
