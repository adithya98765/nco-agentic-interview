# agent.py
from llm import ask_llm

class InterviewAgent:
    def __init__(self, job_info, resume_skills):
        """
        job_info = {
          "Title": "...",
          "NCO_Code": "...",
          "Description": "..."
        }
        """
        self.job_info = job_info
        self.resume_skills = resume_skills
        self.asked = []
        self.confidence = {}

    def decide_next(self):
        prompt = f"""
You are an interview agent.

JOB ROLE (from government NCO data):
Title: {self.job_info['Title']}
NCO Code: {self.job_info['NCO_Code']}
Description: {self.job_info['Description']}

Candidate resume skills:
{self.resume_skills}

Already asked:
{self.asked}

Task:
- Decide the NEXT interview question
- Focus on skills required for the job
- Prefer skills not yet evaluated
- If sufficient confidence is achieved, stop

Respond ONLY in JSON:
{{
  "action": "ask" or "stop",
  "skill": "<skill>",
  "question": "<question>"
}}
"""
        return ask_llm(
            "You are a strict interview agent. Respond only in JSON.",
            prompt
        )

