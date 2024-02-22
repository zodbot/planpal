from datetime import datetime

import pytz

from planpal_agent import gpt_tools
from planpal_agent.assistant import Assistant

instruct_manage_calendar = "use a tool to address the user query to manage the calendar"

local_timezone = datetime.now(pytz.timezone('America/New_York'))  # Replace with your time zone
current_datetime = local_timezone.strftime('%Y-%m-%d %H:%M:%S')
instruct_curr_time = f"today's Date and Time: {current_datetime}, Local Time Zone: {local_timezone}"


class CalendarAssistant(Assistant):
    def __init__(self, client):
        super().__init__(client, "Calendar Assistant")
        self.instructions += instruct_manage_calendar + instruct_curr_time
        self.tools = gpt_tools.tools  # Assuming gpt_tools is defined elsewhere

