from datetime import datetime

import pytz

from planpal_agent.assistant import Assistant

instruct_understand_user = ("task_step: 1" "task_name: Understand User Requirements about time! "
                            "task_objective: Comprehend user-provided task fully and ground time to exact dates"
                            "task_description: Analyze and understand the user's task. generate a right prompt with "
                            "dates in ISO"
                            "8601 format, e.g., '2024-01-10T09:00:00")

local_timezone = datetime.now(pytz.timezone('America/New_York'))  # Replace with your time zone
current_datetime = local_timezone.strftime('%Y-%m-%d %H:%M:%S')
f"today's Date and Time: {current_datetime}, Local Time Zone: {local_timezone}"

instruct_curr_time = f"today's Date and Time: {current_datetime}, Local Time Zone: {local_timezone}"

instruct = ("you only write python code to help the user to find the exact ISO dates for certain time/time period. "
            "You should always write python code as simple as possible to find the dates.")


class InstructAssistant(Assistant):
    def __init__(self, client):
        super().__init__(client, "Time Assistant")
        self.instructions += instruct + instruct_curr_time
        self.tools = [{"type": "code_interpreter"}]

    def construct_prompt(self, user_message):
        return (f"I have a got a request from user, they are asking: {user_message}"
                " I don't know the actual dates they are referring to. can you figure out what the ISO dates are?"
                "if they are referring to multiple days, figure out the start date and duration"
                "Return the date as a string, do not print anything. Please finish this python code: "
                "from datetime import datetime, timedelta # Get today's date today = datetime.now()")
