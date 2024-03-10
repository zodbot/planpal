import json
import time

from openai import OpenAI

client = OpenAI()


def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )


def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")


def create_thread_and_run(user_input, assistant_id):
    thread = client.beta.threads.create()
    run = submit_message(assistant_id, thread, user_input)
    return thread, run


def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(m["role"], ": ", m["content"])
    print()


def extract_assistant_message(messages):
    res = []
    for m in messages:
        res.append({"role": "user",
                    "content": m.content[0].text.value})
    return res


def show_json(obj, write_to_file=False):
    print(json.loads(obj.model_dump_json()))
    parsed_json = json.loads(obj.model_dump_json())

    if write_to_file:
        # Open a file in write mode
        with open('../mid_steps.log', 'a') as file:
            # Write the parsed JSON object to the file
            json.dump(parsed_json, file)
