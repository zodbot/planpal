import json
from datetime import datetime
import pytz

# Assuming gpt_tools, llm, CalendarAssistant, and InstructAssistant are defined elsewhere
from planpal_agent import gpt_tools, llm
from planpal_agent.calendar_assistant import CalendarAssistant
from planpal_agent.ground_instruct_assistant import InstructAssistant

class PlanPalAssistant:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.time_assistant = InstructAssistant(llm_client)
        self.calendar_assistant = CalendarAssistant(llm_client)
        self.TIME_ASSISTANT_ID = self.time_assistant.create_assistant().id
        self.CALENDAR_ASSISTANT_ID = self.calendar_assistant.create_assistant().id

    def process_user_request(self, prompt):
        # Initial response string
        response_str = ""
        # Emulating concurrent user requests for time interpretation
        thread1, run1 = llm.create_thread_and_run(
            self.time_assistant.construct_prompt(prompt),
            self.TIME_ASSISTANT_ID
        )

        # Wait for Run 1: understand the prompt first
        run1 = llm.wait_on_run(run1, thread1)
        response1 = llm.get_response(thread1)
        response_str += llm.pretty_print(response1)
        print("################")

        # Now call the calendar function with the right prompt
        thread2, run2 = llm.create_thread_and_run(
            prompt + llm.extract_assistant_message(response1),
            self.CALENDAR_ASSISTANT_ID
        )
        run2 = llm.wait_on_run(run2, thread2)
        response2 = llm.get_response(thread2)
        response_str = llm.pretty_print(response2)
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

                llm.show_json(run)
                run = llm.wait_on_run(run, thread2)
                response_str = llm.pretty_print(llm.get_response(thread2))
                return response_str
        else:
            return response_str

# Usage example
if __name__ == "__main__":
    llm_client = llm.client  # Assuming llm.client is already defined and configured
    planpal_assistant = PlanPalAssistant(llm_client)
    user_prompt = "user: what do I have scheduled for tomorrow?"
    planpal_assistant.process_user_request(user_prompt)
