from openai import OpenAI
from together import Together
from groq import Groq
class LLM():
    def __init__(self, api_key, model_name="llama3-70b-8192", source="Groq"):
        self.model_name = model_name
        self.api_key = api_key
        self.source = source
        if source == "OpenRouter":
            self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

        if source == "Groq":
            self.client = Groq(api_key=api_key)

        if source == "TogetherAI":
            self.client = Together(api_key=api_key)

    def generate(self, system_prompt, user_prompt):
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )
        return completion.choices[0].message.content