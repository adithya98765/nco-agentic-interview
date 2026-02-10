# resume_parser.py
import re

def extract_skills(text):
    match = re.search(r"Skills:(.*?)(Projects:|Education:|$)", text, re.S)
    if not match:
        return []
    skills = re.findall(r"- (.+)", match.group(1))
    return [s.strip() for s in skills]

