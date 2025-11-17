""" 
Plik w ktorym:
- wysyłamy oferte pracy
- przekazujemy przetworzone cv
- prosimy o wybranie najlpiej dopasowanego cv

"""

from config import AzureConfig, GPTMatcherConfig
import json

class Matcher():
    def __init__(self):
        self.client = AzureConfig.get_openai_client()
        self.deployment_name = AzureConfig.OPENAI_DEPLOYMENT_NAME

    def _system_message(self):
        return {
            "role": "system",
            "content": GPTMatcherConfig.SYSTEM_PROMPT
        }


    def _user_message(self, cvs, job_offer):

        prompt = f"""
        You will receive:
        1) Job offer
        2) List of candidate CV JSONs

        You MUST return a JSON ranking the top 3 candidates. 

        Job offer:
        {job_offer}

        CVs:
        {json.dumps(cvs)}
        """
    
        return {
            "role": "user",
            "content": prompt
            }


    def match(self, job_offer: str, cv_list: list):
        system_msg = self._system_message()
        user_msg = self._user_message(cvs=cv_list, job_offer=job_offer)
        messages = [system_msg, user_msg]

        response = self.client.chat.completions.create(
        model=self.deployment_name,
        messages=messages,
        temperature=GPTMatcherConfig.TEMPERATURE,
        max_tokens=GPTMatcherConfig.MAX_TOKENS
    )

        content = response.choices[0].message.content

        try:
            result = json.loads(content)
            return result
        except Exception:
            print("GPT did not return valid JSON. Raw output:")
            print(content)
            return None
