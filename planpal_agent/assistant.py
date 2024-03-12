general_instruct = (
    "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request "
    "is ambiguous.")


class Assistant:
    def __init__(self, client, name):
        self.client = client
        self.name = name
        self.instructions = general_instruct
        self.tools = []
        self.model = "gpt-4-1106-preview"

    def create_assistant(self):
        return self.client.beta.assistants.create(
            name=self.name,
            instructions=self.instructions,
            tools=self.tools,
            model=self.model,

        )
