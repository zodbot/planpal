import json
from datetime import datetime

import pytz

from planpal_agent import gpt_tools, llm
from planpal_agent.calendar_assistant import CalendarAssistant
from planpal_agent.ground_instruct_assistant import InstructAssistant


time_assistant = InstructAssistant(llm.client)
calendar_assistant = CalendarAssistant(llm.client)
TIME_ASSISTANT_ID = time_assistant.create_assistant().id
CALENDAR_ASSISTANT_ID = calendar_assistant.create_assistant().id

prompt = "user: what do I have schedule for tomorrow?  "
# Emulating concurrent user requests
thread1, run1 = llm.create_thread_and_run(
    time_assistant.construct_prompt(prompt),
    TIME_ASSISTANT_ID
)

# # Wait for Run 1: understand the prompt first
run1 = llm.wait_on_run(run1, thread1)
response1 = llm.get_response(thread1)
llm.pretty_print(response1)
print("################")

run_steps = llm.client.beta.threads.runs.steps.list(
    thread_id=thread1.id, run_id=run1.id, order="asc"
)

#
# for step in run_steps.data:
#     step_details = step.step_details
#     response_str = response_str + step_details.__str__()
#     print(json.dumps(llm.show_json(step_details), indent=4))

# now call the calendar function with the right prompt
thread2, run2 = llm.create_thread_and_run(
    prompt + llm.extract_assistant_message(response1),
    CALENDAR_ASSISTANT_ID
)
run2 = llm.wait_on_run(run2, thread2)
response2 = llm.get_response(thread2)
llm.pretty_print(response2)

tool_calls = run2.required_action.submit_tool_outputs.tool_calls
tool_response = ""
for tool_call in tool_calls:
    function_name = tool_call.function.name

    function_args = json.loads(tool_call.function.arguments)
    print("function args: ", function_args)
    tool_response = gpt_tools.function_call(function_name, function_args)
    # print(tool_response)

    run = llm.client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread2.id,
        run_id=run2.id,
        tool_outputs=[
            {
                "tool_call_id": tool_call.id,
                "output": json.dumps(tool_response),
            }
        ],
    )

    llm.show_json(run)
    run = llm.wait_on_run(run, thread2)
    llm.pretty_print(llm.get_response(thread2))

# TODO: when it fails, it should know why it fails and generate code to fix it! or ask for help!
# TODO: write previous codes in cases! and retrieve that first! if not exist, generate new code
# TODO: something to decide which assitant to call!