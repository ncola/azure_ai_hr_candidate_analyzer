""" 
Plik w ktorym:
- wysyłamy oferte pracy
- przekazujemy przetworzone cv
- prosimy o wybranie najlpiej dopasowanego cv

"""

from ..azure_services.openai_client import AzureOpenAIClient

class Matcher():
    def __init__(self):
        self.client = AzureOpenAIClient()

    def _system_message(self):
        
        system_message = "You are an AI HR assistant that evaluates how well a candidate matches a job posting. You analyze both the candidate’s CV and the job description, identify matching skills and missing ones."
        return {
            "role": "system",
            "content": [
                {"type": "input_text", "text": system_message.strip()}
            ],
        }

    def _user_message(self, cvs: list, job_offer:str):
        cv = [
            {"type": "input_text", "text": cv}
            ]
        job_offer = [
            {"type": "input_text", "text": job_offer}
        ]

        for cv in cvs:
            cv_list = []
            template_cv_input = {"type": "input_text", "text": cv}
            cv_list.append(template_cv_input)

        final = {
            "role": "user",
            "content": [
                *cv_list, job_offer
            ]
        }
        return final


    def match(self, job_offer:str, cv_list:list):
        system_msg = self._system_message()
        user_msg = self._user_message(cvs=cv_list, job_offer=job_offer)
        input = [system_msg, user_msg]
        self.client.ask_question(
            input = input
        )
