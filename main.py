# main.py
from resume_parser import extract_skills
from faiss_search import NCOSemanticSearch
from agent import InterviewAgent

# Load resume
resume_text = open("resumes/resume1.txt").read()
resume_skills = extract_skills(resume_text)

# Semantic job search
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

# Start interview
decision = agent.decide_next()

while decision["action"] != "stop":
    print("\nQuestion:", decision["question"])

    answer = input("Your answer: ")

    # Evaluate answer
    evaluation = agent.evaluate_answer(answer)

    print("\nScore:", evaluation["score"])
    print("Level:", evaluation["level"])
    print("Feedback:", evaluation["reason"])

    # Decide next step
    decision = agent.next_step_after_evaluation(evaluation)

print("\nInterview complete.")