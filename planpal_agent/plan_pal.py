import json
from datetime import datetime
import pytz

# Assuming gpt_tools, llm, CalendarAssistant, and InstructAssistant are defined elsewhere
from planpal_agent import gpt_tools, llm
from planpal_agent.calendar_assistant import CalendarAssistant
from planpal_agent.ground_instruct_assistant import InstructAssistant
from logger import get_logger


class PlanPalAssistant:
    def __init__(self, llm_client):
        self.logger = get_logger(self.__class__.__name__)
        self.llm_client = llm_client
        self.time_assistant = InstructAssistant(llm_client)
        self.calendar_assistant = CalendarAssistant(llm_client)
        self.TIME_ASSISTANT_ID = self.time_assistant.create_assistant().id
        self.CALENDAR_ASSISTANT_ID = self.calendar_assistant.create_assistant().id

    def process_user_request(self, prompt, history=None, max_history_messages=5):
        messages = []
        if history:
            print("history: ", history)
            # Limit the history to the last max_history_messages messages
            # thread already handles this, but I still limit the messages for testing.
            limited_history = history[-max_history_messages:]
            messages = limited_history + messages

        messages.append(self.time_assistant.construct_prompt(user_message=prompt))
        self.logger.debug("the first prompt to time assistant: ", messages)

        thread1 = self.llm_client.beta.threads.create(
            messages=messages
        )
        # Emulating concurrent user requests for time interpretation
        run1 = self.llm_client.beta.threads.runs.create(
            thread_id=thread1.id,
            assistant_id=self.TIME_ASSISTANT_ID,
        )
        # Wait for Run 1: understand the prompt first
        llm.wait_on_run(run1, thread1)

        response1 = llm.get_response(thread1)
        # messages = llm.extract_assistant_message(response1)
        #

        # Now call the calendar function with the right prompt
        # thread2, run2 = llm.create_thread_and_run(
        #     prompt + llm.extract_assistant_message(response1),
        #     self.CALENDAR_ASSISTANT_ID
        # )
        new_prompt = [{
            "role": "user",
            "content": prompt
        }]
        new_messages = llm.extract_assistant_message(response1) + new_prompt

        thread2 = self.llm_client.beta.threads.create(
            messages=new_messages
        )
        # Emulating concurrent user requests for time interpretation
        run2 = self.llm_client.beta.threads.runs.create(
            thread_id=thread2.id,
            assistant_id=self.CALENDAR_ASSISTANT_ID
        )

        run2 = llm.wait_on_run(run2, thread2)
        response2 = llm.get_response(thread2)
        messages = llm.extract_assistant_message(response2)

        # response_str = llm.pretty_print(response2)
        if run2.required_action:
            # Process tool calls from the calendar response
            tool_calls = run2.required_action.submit_tool_outputs.tool_calls
            tool_response = ""
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                print("Function args: ", function_args)
                tool_response = gpt_tools.function_call(function_name, function_args)

                run = llm.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread2.id,
                    run_id=run2.id,
                    tool_outputs=[
                        {"tool_call_id": tool_call.id, "output": json.dumps(tool_response)},
                    ],
                )

                llm.wait_on_run(run, thread2)

                messages = llm.extract_assistant_message(llm.get_response(thread2))
                return messages
        else:
            return messages


# Usage example
if __name__ == "__main__":
    llm_client = llm.client  # Assuming llm.client is already defined and configured
    planpal_assistant = PlanPalAssistant(llm_client)
    p = "user: add to my calander that I go shopping on tuesday?"
    h = planpal_assistant.process_user_request(p)

    p1 = "at 6pm"
    h2 = planpal_assistant.process_user_request(p1, h)
