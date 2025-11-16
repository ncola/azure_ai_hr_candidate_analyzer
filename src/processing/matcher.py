""" 
Plik w ktorym:
- wysyłamy oferte pracy
- przekazujemy przetworzone cv
- prosimy o wybranie najlpiej dopasowanego cv

"""

from config import AzureConfig
import json

class Matcher():
    def __init__(self):
        self.client = AzureConfig.get_openai_client()
        self.deployment_name = AzureConfig.OPENAI_DEPLOYMENT_NAME

    def _system_message(self):
        system_message = """
            You are an AI HR assistant that compares job descriptions with multiple candidate CVs.
            You MUST return output strictly as JSON, compact, with no explanations, markdown, or formatting.

            Focus ONLY on the skills section. For each CV:
            - matched_skills: skills literally present both in the CV and required by the job
            - missing_skills: skills required by the job but not present in CV

            Only consider skills literally listed in the job offer and in the candidate's CV, without any additional or assumed skills.

            Sort candidates by score descending and return ONLY the top 3 candidates. The best candidate is the one that matches the most required skills.

            Return JSON strictly in this structure:

            {
            "top_3": [
                {
                "candidate_id": "candidate number",
                "matched_skills": ["skill1", "skill2"],
                "missing_skills": ["skill3"]
            }
        ]
        } 
            """
        
        return {
            "role": "system",
            "content": system_message.strip()
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
        temperature=0.0,
        max_tokens=2000
    )

        content = response.choices[0].message.content

        try:
            result = json.loads(content)
            return result
        except Exception:
            print("GPT did not return valid JSON. Raw output:")
            print(content)
            return None
