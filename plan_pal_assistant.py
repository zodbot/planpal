import logging
import os
from logger import get_logger

import openai
import requests
from openai import OpenAI
import json
from termcolor import colored
from tenacity import retry, wait_random_exponential, stop_after_attempt
from datetime import datetime
import pytz

from planpal_agent import gpt_tools
from my_calendar import MyCalendar
from dotenv import load_dotenv

import os

GPT_MODEL = "gpt-4"


class PlanPal:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.client = OpenAI()
        # Load environment variables from .env file
        load_dotenv(".env")

        # Ensure your OpenAI API key is loaded from the environment variables
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.cal = MyCalendar()

    def get_calendar_events(self, n):
        print("called get_calendar_events function! ")
        events = self.cal.get_events(n=n)
        return json.dumps({"events": events})

    def get_calendar_events_n_days(self, n_days):
        print("called get_calendar_events function! ")
        events = self.cal.get_events_n_days(n_days)
        return json.dumps({"events": events})

    def create_calendar_event(self, start_time, summary, duration=1, description=None, location=None):
        details = self.cal.create_event(start_time, summary, duration, description, location)
        print("called create_calendar_event function! ")
        return json.dumps({"details": details})

    def pretty_print_conversation(self, messages):
        role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "tool": "magenta",
        }

        for message in messages:
            if message['role'] == "system":
                print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
            elif message['role'] == "user":
                print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
            elif message['role'] == "assistant" and message.get("function_call"):
                print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
            elif message['role'] == "assistant" and not message.get("function_call"):
                print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
            elif message['role'] == "tool":
                print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))

    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    def chat_completion_request(self, messages, tools=None, tool_choice=None, model=GPT_MODEL):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + openai.api_key,
        }
        json_data = {"model": model, "messages": messages}
        if tools is not None:
            json_data.update({"tools": tools})
        if tool_choice is not None:
            json_data.update({"tool_choice": tool_choice})
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=json_data,
            )
            return response
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e

    def run_conversation(self, user_input, history:dict = None, max_history_messages=20):
        self.logger.debug("user prompt", user_input)

        local_timezone = datetime.now(pytz.timezone('America/New_York'))  # Replace with your time zone
        current_datetime = local_timezone.strftime('%Y-%m-%d %H:%M:%S')

        # Step 1: send the conversation and available functions to the model
        messages = [{"role": "system",
                     "content": "Don't make assumptions about what values to plug into functions. Ask for "
                                "clarification if a user request is ambiguous."},
                    {"role": "system",
                     "content": "The user must specify time and date in the request. Ask for time or date if it is not "
                                "specified! Don't make time or date up"},

                    {"role": "system",
                     "content": f"Current Date and Time: {current_datetime}, Local Time Zone: {local_timezone}"
                     }]
        # If there's history, prepend it to the current session's messages
        # If history is provided, integrate its messages at the beginning
        if history:
            # Limit the history to the last max_history_messages messages
            limited_history = history['messages'][-max_history_messages:]
            messages = limited_history + messages

        # Append the new user input to the conversation
        messages.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages,
            tools=gpt_tools.tools,
            temperature=0.0,
            tool_choice="auto",  # auto is default, but we'll be explicit
        )
        response_message = response.choices[0].message

        simulated_response = {"role": "assistant", "content": response_message}
        messages.append(simulated_response)

        self.pretty_print_conversation(messages)

        tool_calls = response_message.tool_calls
        self.logger.debug("tool_calls", tool_calls)

        if not tool_calls:
            self.pretty_print_conversation(messages)
            return messages

        # Step 2: check if the model wanted to call a function

            # messages.append(response_message)  # extend conversation with assistant's reply
            # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = gpt_tools.available_functions[function_name]
            self.logger.debug(function_to_call)
            function_args = json.loads(tool_call.function.arguments)
            function_response = ""
            if function_name == 'fetch_event_date':
                # Extract 'date' parameter for get_events function
                date = function_args.get("date")
                function_response = function_to_call(date=date)
                self.logger.debug(function_response)

            elif function_name == 'get_events_n_days':
                # Extract 'n' parameter for get_events function
                n = function_args.get("n")
                function_response = function_to_call(n_days=n)
                self.logger.debug(function_response)

            elif function_name == 'create_event':
                # Extract parameters for add_event function
                start_time = function_args.get("start_time")
                summary = function_args.get("summary")
                duration = function_args.get("duration")
                description = function_args.get("description")
                location = function_args.get("location")

                function_response = function_to_call(
                    start_time=start_time,
                    summary=summary,
                    duration=duration,
                    description=description,
                    location=location
                )
                self.logger.debug(function_response)
                #
            if function_response:
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )  # extend conversation with function response
            second_response = self.client.chat.completions.create(
                model=GPT_MODEL,
                temperature=0,
                messages=messages,
            )  # get a new response from the model where it can see the function response

            messages.append(
                {
                    "role": "assistant",
                    "content": second_response,
                })
            self.pretty_print_conversation(messages)

            return messages

p = PlanPal()
p.run_conversation("what is on my calander tomorrow?")