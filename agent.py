# agent.py
import json
from llm import ask_llm


class InterviewAgent:
    def __init__(self, job_info, resume_skills):
        self.job_info = job_info
        self.resume_skills = resume_skills
        self.asked = []
        self.confidence = {}
        self.last_skill = None
        self.last_question = None
        self.answer_history = []   # NEW: for risk detection

    # -----------------------------
    # 1. DECIDE NEXT QUESTION
    # -----------------------------
    def decide_next(self):
        prompt = f"""
You are an intelligent interview agent.

JOB ROLE:
Title: {self.job_info['Title']}
Description: {self.job_info['Description']}

Candidate skills:
{self.resume_skills}

Already asked:
{self.asked}

Skill confidence so far:
{self.confidence}

Rules:
- Ask a mix of:
  * Technical questions
  * Behavioral questions
  * Scenario-based questions (IMPORTANT)
- Prefer skills with LOW confidence
- Avoid repeating questions
- Make questions practical and reasoning-based
- If all important skills are evaluated, STOP

Respond ONLY in JSON:
{{
  "action": "ask" or "stop",
  "skill": "<skill>",
  "question": "<question>"
}}
"""
        response = ask_llm(
            "You are a strict interview agent. Respond only in JSON.",
            prompt
        )

        data = self._safe_json(response)

        if data["action"] == "ask":
            self.last_skill = data["skill"]
            self.last_question = data["question"]
            self.asked.append(data["question"])

        return data

    # -----------------------------
    # 2. EVALUATE ANSWER
    # -----------------------------
    def evaluate_answer(self, answer):
        prompt = f"""
You are an expert technical interviewer.

JOB ROLE:
{self.job_info['Title']}

Skill:
{self.last_skill}

Question:
{self.last_question}

Candidate Answer:
{answer}

Evaluate based on:
- relevance
- correctness
- depth
- clarity

Respond ONLY in JSON:
{{
  "score": 0 to 1,
  "level": "poor / average / good / excellent",
  "reason": "short explanation",
  "follow_up": "next question if needed"
}}
"""
        response = ask_llm(
            "You are a strict evaluator. Respond only in JSON.",
            prompt
        )

        data = self._safe_json(response)

        score = float(data.get("score", 0))

        # Update confidence
        self.confidence[self.last_skill] = score

        # Store answer for risk detection
        self.answer_history.append(answer)

        return data

    # -----------------------------
    # 3. FOLLOW-UP LOGIC
    # -----------------------------
    def next_step_after_evaluation(self, evaluation):
        score = float(evaluation.get("score", 0))

        # Low score → same skill (simpler follow-up)
        if score < 0.5:
            return {
                "action": "ask",
                "skill": self.last_skill,
                "question": evaluation.get(
                    "follow_up",
                    "Can you explain that more clearly?"
                )
            }

        # Medium score → deeper follow-up
        elif score < 0.8:
            return {
                "action": "ask",
                "skill": self.last_skill,
                "question": evaluation.get(
                    "follow_up",
                    "Let's go deeper into this concept."
                )
            }

        # High score → move to next skill
        else:
            return self.decide_next()

    # -----------------------------
    # 4. AI RISK DETECTION (NEW)
    # -----------------------------
    def compute_risk_score(self):
        answers = self.answer_history

        if len(answers) < 2:
            return {"risk": "LOW", "score": 0.1}

        # 1. Repetition check
        unique_ratio = len(set(answers)) / len(answers)

        # 2. Length consistency
        lengths = [len(a.split()) for a in answers]
        variance = max(lengths) - min(lengths)

        # 3. Overly long answers (possible AI)
        long_answers = all(len(a.split()) > 40 for a in answers)

        risk_score = 0

        if unique_ratio < 0.7:
            risk_score += 0.4

        if variance < 5:
            risk_score += 0.3

        if long_answers:
            risk_score += 0.3

        if risk_score > 0.7:
            return {"risk": "HIGH", "score": risk_score}
        elif risk_score > 0.4:
            return {"risk": "MEDIUM", "score": risk_score}
        else:
            return {"risk": "LOW", "score": risk_score}

    # -----------------------------
    # 5. SAFE JSON PARSER
    # -----------------------------
    def _safe_json(self, text):
        try:
            return json.loads(text)
        except:
            try:
                start = text.find("{")
                end = text.rfind("}") + 1
                return json.loads(text[start:end])
            except:
                return {
                    "action": "ask",
                    "skill": "general",
                    "question": "Tell me about your experience."
                }