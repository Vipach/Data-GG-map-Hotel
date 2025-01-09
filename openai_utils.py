import time
import openai

class Message:
    def __init__(self, sys_content, prompt, json_answer):
        self.sys_content = sys_content
        self.prompt = prompt
        self.json_answer = json_answer

    def to_list(self):
        final_prompt = f"{self.prompt}\nResponse in JSON format:\n{self.json_answer}"
        return [
            {"role": "system", "content": self.sys_content},
            {"role": "user", "content": final_prompt}
        ]

class OpenAIClient:
    def __init__(self, sys_content, model='gpt-4'):
        self.model = model
        self.api_key = self.get_key()
        self.sys_content = sys_content

    def get_key(self):
        with open('key.txt') as f:
            return f.read().strip()

    def answer(self, prompt, json_answer):
        msg = Message(self.sys_content, prompt, json_answer)
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=msg.to_list(),
            api_key=self.api_key
        )
        return response['choices'][0]['message']['content'].strip()

class OpenAIAssistant:
    """
    A class representing an OpenAI Assistant.

    Attributes:
        threads (Threads): The threads API object.
        assistants (Assistants): The assistants API object.
        assistant (Assistant): The created assistant.
        thread (Thread): The created thread.
        assistant_messages (list): A list of assistant messages.
        user_messages (list): A list of user messages.

    Methods:
        __init__(self, model_name, init_instruction, model='gpt-4o'): Initializes the OpenAIAssistant object.
        get_key(self): Retrieves the API key from the 'key.txt' file.
        add_message(self, role, content): Adds a message to the thread.
        delete_messages(self, role): Deletes all messages of the specified role from the thread.
        delete_message(self, role, message_id): Deletes a specific message from the thread.
        run_question(self, question, answer_format=None, custom_instruction=None): Runs a question and retrieves the assistant's response.
        assistant_response_from_run(self, run): Retrieves the assistant's response from a run.
        answer(self, question, answer_format=None, custom_instruction=None): Asks a question and returns the assistant's response.
    """

    def __init__(self, model_name, init_instruction, model='gpt-4o'):
        """
        Initializes the OpenAIAssistant object.

        Args:
            model_name (str): The name of the model.
            init_instruction (str): The initial instruction for the assistant.
            model (str, optional): The model to use. Defaults to 'gpt-4o'.
        """
        self.model_name = model_name
        self.init_instruction = init_instruction
        self.model = model
        self.api_key = self.get_key()
        self.assistant_messages = []
        self.user_messages = []

    def get_key(self):
        """
        Retrieves the API key from the 'key.txt' file.

        Returns:
            str: The API key.
        """
        with open('key.txt') as f:
            return f.read().strip()

    def add_message(self, role, content):
        """
        Adds a message to the thread.

        Args:
            role (str): The role of the message ('assistant' or 'user').
            content (str): The content of the message.
        """
        msg = {"role": role, "content": content}
        if role == 'assistant':
            self.assistant_messages.append(msg)
        else:
            self.user_messages.append(msg)

    def delete_messages(self, role):
        """
        Deletes all messages of the specified role from the thread.

        Args:
            role (str): The role of the messages to delete ('assistant' or 'user').
        """
        if role == 'assistant':
            self.assistant_messages = []
        else:
            self.user_messages = []

    def delete_message(self, role, message_id):
        """
        Deletes a specific message from the thread.

        Args:
            role (str): The role of the message ('assistant' or 'user').
            message_id (str): The ID of the message to delete.
        """
        if role == 'assistant':
            self.assistant_messages = [
                msg for msg in self.assistant_messages if msg.get('id') != message_id
            ]
        else:
            self.user_messages = [
                msg for msg in self.user_messages if msg.get('id') != message_id
            ]

    def run_question(self, question, answer_format=None, custom_instruction=None):
        """
        Runs a question and retrieves the assistant's response.

        Args:
            question (str): The question to ask the assistant.
            answer_format (str, optional): The desired format for the answer. Defaults to None.
            custom_instruction (str, optional): Custom instructions for the assistant. Defaults to None.

        Returns:
            dict: The response object containing the assistant's response.
        """
        if answer_format:
            question += f"\nResponse in following format: {answer_format}"

        # Add user message to the thread
        self.add_message('user', question)

        # Call the OpenAI API to get the assistant's response
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.init_instruction},
                *self.user_messages,
                *self.assistant_messages
            ],
            api_key=self.api_key
        )
        
        # Simulate waiting for the response
        count = 0
        while True:
            if count >= 15:
                self.delete_messages('user')
                return self.run_question(question, answer_format, custom_instruction)
            time.sleep(2)
            count += 1
            break
        
        return response

    def assistant_response_from_run(self, run):
        """
        Retrieves the assistant's response from a run.

        Args:
            run (dict): The response object.

        Returns:
            str: The assistant's response.
        """
        if run:
            return run['choices'][0]['message']['content']
        return None

    def answer(self, question, answer_format=None, custom_instruction=None):
        """
        Asks a question and returns the assistant's response.

        Args:
            question (str): The question to ask the assistant.
            answer_format (str, optional): The desired format for the answer. Defaults to None.
            custom_instruction (str, optional): Custom instructions for the assistant. Defaults to None.

        Returns:
            str: The assistant's response.
        """
        run = self.run_question(question, answer_format, custom_instruction)
        return self.assistant_response_from_run(run)
