# main.py
from resume_parser import extract_skills
from faiss_search import NCOSemanticSearch
from agent import InterviewAgent

# Load resume
resume_text = open("resumes/resume1.txt").read()
resume_skills = extract_skills(resume_text)

# Semantic job search (your old project)
searcher = NCOSemanticSearch()
job_matches = searcher.search("software engineer", k=1)

top_job = job_matches[0]

print("\nTop matched job:")
print(top_job)

# Initialize agent
agent = InterviewAgent(
    job_info=top_job,
    resume_skills=resume_skills
)

# Interview loop
while True:
    decision = agent.decide_next()
    print("\nAGENT DECISION:\n", decision)

    if '"action": "stop"' in decision:
        print("\nInterview complete.")
        break

    question = decision.split('"question":')[1].split('"')[1]
    print("\nQUESTION:", question)

    answer = input("\nYour answer: ")

