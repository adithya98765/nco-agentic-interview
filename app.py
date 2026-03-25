import streamlit as st
import json
import sys
import os

try:
    from resume_parser import extract_skills
    from faiss_search import NCOSemanticSearch
    from agent import InterviewAgent
except ImportError as e:
    st.error(f"Import Error: {str(e)} - Please install missing dependencies.")
    st.stop()

st.set_page_config(
    page_title="NCO Interview Agent",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .agent-message {
        background-color: #E8F4F8;
        border-left: 4px solid #0083B8;
    }
    .user-message {
        background-color: #E8F8E8;
        border-left: 4px solid #00A84F;
    }
    .skill-badge {
        display: inline-block;
        background-color: #F0F0F0;
        padding: 0.3rem 0.6rem;
        border-radius: 0.3rem;
        margin: 0.2rem;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

# SESSION STATE
if "interview_initialized" not in st.session_state:
    st.session_state.interview_initialized = False
    st.session_state.agent = None
    st.session_state.job_info = None
    st.session_state.resume_skills = None
    st.session_state.messages = []
    st.session_state.interview_complete = False
    st.session_state.asked_skills = []


def initialize_interview():
    try:
        with open("resumes/resume1.txt") as f:
            resume_text = f.read()
        resume_skills = extract_skills(resume_text)

        searcher = NCOSemanticSearch()
        job_matches = searcher.search("software engineer", k=1)
        top_job = job_matches[0]

        agent = InterviewAgent(
            job_info=top_job,
            resume_skills=resume_skills
        )

        st.session_state.agent = agent
        st.session_state.job_info = top_job
        st.session_state.resume_skills = resume_skills
        st.session_state.interview_initialized = True
        st.session_state.messages = []
        st.session_state.interview_complete = False
        st.session_state.asked_skills = []

        return True
    except Exception as e:
        st.error(f"Error initializing interview: {str(e)}")
        return False


def get_next_question():
    if st.session_state.agent is None:
        return None
    try:
        return st.session_state.agent.decide_next()
    except Exception as e:
        st.error(f"Error getting next question: {str(e)}")
        return None


def start_interview():
    decision = get_next_question()

    if decision:
        if decision.get("action") == "stop":
            st.session_state.interview_complete = True
            st.session_state.messages.append({
                "role": "agent",
                "content": "Interview complete! Thank you."
            })
        else:
            question = decision.get("question", "")
            skill = decision.get("skill", "")
            if question:
                st.session_state.asked_skills.append(skill)
                st.session_state.messages.append({
                    "role": "agent",
                    "content": question,
                    "skill": skill
                })


# SIDEBAR
with st.sidebar:
    st.title("📋 Interview Info")

    if st.session_state.interview_initialized:
        st.subheader("Job Role")
        st.write(f"**Title:** {st.session_state.job_info['Title']}")
        st.write(f"**Code:** {st.session_state.job_info['NCO_Code']}")

        with st.expander("Job Description"):
            st.write(st.session_state.job_info['Description'])

        st.divider()

        st.subheader("Your Skills")
        if st.session_state.resume_skills:
            skills = st.session_state.resume_skills
            if isinstance(skills, list):
                display_skills = ", ".join(skills)
            else:
                display_skills = skills
            st.text_area("Extracted Skills:", value=display_skills, height=200, disabled=True)

        st.divider()

        st.subheader("Interview Progress")

        agent = st.session_state.agent
        skills = st.session_state.resume_skills or []
        if isinstance(skills, list):
            total_skills = len(skills)
        else:
            total_skills = len(skills.split(","))

        done_skills = len(agent.confidence) if agent else 0

        progress = done_skills / max(total_skills, 1)

        st.progress(progress)
        st.write(f"{done_skills}/{total_skills} skills evaluated")

        if st.session_state.asked_skills:
            for i, skill in enumerate(st.session_state.asked_skills, 1):
                st.write(f"{i}. {skill}")

    else:
        st.info("Initialize interview to see details.")


# MAIN UI
st.title("🎤 NCO Interview Agent")

if not st.session_state.interview_initialized:
    st.subheader("Welcome to the Interview System")

    col1, col2 = st.columns(2)

    with col1:
        st.info("""
        This system will:
        1. Analyze your resume
        2. Match you to a relevant job role
        3. Conduct an adaptive interview
        """)

    with col2:
        if st.button("Start Interview", type="primary", use_container_width=True):
            with st.spinner("Initializing interview..."):
                if initialize_interview():
                    st.success("Interview initialized successfully!")
                    st.rerun()

else:
    st.subheader("Interview Chat")

    for msg in st.session_state.messages:
        if msg["role"] == "agent":
            with st.chat_message("assistant", avatar="🤖"):
                st.write(msg["content"])
                if "skill" in msg:
                    st.caption(f"📌 Evaluating: {msg['skill']}")
        else:
            with st.chat_message("user", avatar="👤"):
                st.write(msg["content"])

    if not st.session_state.interview_complete:

        # 🔴 EXIT BUTTON
        if st.button("🛑 End Interview", use_container_width=True):
            st.session_state.interview_complete = True
            st.rerun()

        if not st.session_state.messages:
            if st.button("Get First Question", use_container_width=True):
                start_interview()
                st.rerun()

        else:
            col1, col2 = st.columns([0.9, 0.1])

            with col1:
                user_input = st.text_input(
                    "Your answer:",
                    placeholder="Type your response here...",
                    label_visibility="collapsed",
                    key=f"input_{len(st.session_state.messages)}"
                )

            with col2:
                submit_button = st.button("Send", use_container_width=True)

            # ⚡ DEMO MODE
            if st.button("⚡ Auto Answer (Demo Mode)"):
                user_input = "This is a structured answer demonstrating understanding of the concept."
                submit_button = True

            if submit_button and user_input:
                agent = st.session_state.agent

                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input
                })

                with st.spinner("Evaluating answer..."):

                    evaluation = agent.evaluate_answer(user_input)

                    st.session_state.messages.append({
                        "role": "agent",
                        "content": f"""
**Score:** {evaluation.get("score", 0):.2f}  
**Level:** {evaluation.get("level", "")}  

**Feedback:**  
{evaluation.get("reason", "")}
"""
                    })

                    decision = agent.next_step_after_evaluation(evaluation)

                    if decision["action"] == "stop":
                        st.session_state.interview_complete = True
                        st.session_state.messages.append({
                            "role": "agent",
                            "content": "✅ Interview complete. Great job!"
                        })
                    else:
                        question = decision["question"]
                        skill = decision.get("skill", "")

                        st.session_state.asked_skills.append(skill)

                        st.session_state.messages.append({
                            "role": "agent",
                            "content": question,
                            "skill": skill
                        })

                st.rerun()

    else:
        st.success("✅ Interview Complete!")

        agent = st.session_state.agent
        scores = agent.confidence

        if scores:
            interview_score = sum(scores.values()) / len(scores)
        else:
            interview_score = 0

        skills = st.session_state.resume_skills or []
        if isinstance(skills, list):
            skill_count = len(skills)
        else:
            skill_count = len(skills.split(","))

        resume_score = min(1.0, skill_count / 10)
        risk_data = agent.compute_risk_score()
        risk_penalty = risk_data["score"] * 0.1

        final_score = (
            0.5 * resume_score +
            0.4 * interview_score -
            0.1 * risk_penalty
        )

        st.subheader("📊 Final Results")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Resume Score", f"{resume_score:.2f}")

        with col2:
            st.metric("Interview Score", f"{interview_score:.2f}")

        with col3:
            st.metric("Final Score", f"{final_score:.2f}")

        st.divider()

        st.subheader("🧠 Skill Evaluation")
        for skill, score in scores.items():
            st.write(f"{skill}: {score:.2f}")

        st.subheader("📈 Performance Analysis")

        strong = [k for k, v in scores.items() if v > 0.75]
        weak = [k for k, v in scores.items() if v < 0.5]

        st.write("**Strengths:**", strong if strong else "None")
        st.write("**Weak Areas:**", weak if weak else "None")

        st.subheader("⚠️ AI Risk Analysis")

        st.write(f"Risk Level: **{risk_data['risk']}**")
        st.write(f"Risk Score: {risk_data['score']:.2f}")

        st.subheader("🕵️ Behavior Monitoring (Simulated)")
        tab_switches = len(st.session_state.messages) // 3
        st.write(f"Tab switches detected: {tab_switches}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Start New Interview", use_container_width=True):
                st.session_state.interview_initialized = False
                st.session_state.messages = []
                st.rerun()

        with col2:
            if st.button("Download Summary", use_container_width=True):
                summary = f"""
INTERVIEW SUMMARY
=================

Job Role: {st.session_state.job_info['Title']}
Job Code: {st.session_state.job_info['NCO_Code']}

Final Score: {final_score:.2f}

Skills Evaluated:
{chr(10).join([f"- {skill}" for skill in st.session_state.asked_skills])}

Interview Transcript:
{chr(10).join([f"{msg['role'].upper()}: {msg['content']}" for msg in st.session_state.messages])}
"""
                st.download_button(
                    label="Download Summary",
                    data=summary,
                    file_name="interview_summary.txt",
                    mime="text/plain"
                )