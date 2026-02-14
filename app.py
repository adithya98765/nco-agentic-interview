import streamlit as st
import json
import sys
import os

# Add proper error handling for imports
try:
    from resume_parser import extract_skills
    from faiss_search import NCOSemanticSearch
    from agent import InterviewAgent
except ImportError as e:
    st.error(f"Import Error: {str(e)} - Please install missing dependencies.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="NCO Interview Agent",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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

# Initialize session state
if "interview_initialized" not in st.session_state:
    st.session_state.interview_initialized = False
    st.session_state.agent = None
    st.session_state.job_info = None
    st.session_state.resume_skills = None
    st.session_state.messages = []
    st.session_state.interview_complete = False
    st.session_state.asked_skills = []


def initialize_interview():
    """Initialize the interview with resume and job matching."""
    try:
        # Load resume
        with open("resumes/resume1.txt") as f:
            resume_text = f.read()
        resume_skills = extract_skills(resume_text)
        
        # Semantic job search
        searcher = NCOSemanticSearch()
        job_matches = searcher.search("software engineer", k=1)
        top_job = job_matches[0]
        
        # Initialize agent
        agent = InterviewAgent(
            job_info=top_job,
            resume_skills=resume_skills
        )
        
        # Store in session state
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
    """Get the next question from the agent."""
    if st.session_state.agent is None:
        return None
    
    try:
        decision = st.session_state.agent.decide_next()
        return decision
    except Exception as e:
        st.error(f"Error getting next question: {str(e)}")
        return None


def start_interview():
    """Start a new interview by getting the first question."""
    if not st.session_state.interview_initialized:
        return
    
    # Get first question
    decision = get_next_question()
    
    if decision:
        try:
            # Parse the decision
            decision_json = json.loads(decision)
            
            if decision_json.get("action") == "stop":
                st.session_state.interview_complete = True
                st.session_state.messages.append({
                    "role": "agent",
                    "content": "Interview complete! Thank you for answering all the questions."
                })
            else:
                question = decision_json.get("question", "")
                skill = decision_json.get("skill", "")
                if question:
                    st.session_state.asked_skills.append(skill)
                    st.session_state.messages.append({
                        "role": "agent",
                        "content": question,
                        "skill": skill
                    })
        except json.JSONDecodeError:
            st.error("Error parsing agent response. Please try again.")


# Sidebar for job and resume info
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
            skills_text = st.session_state.resume_skills
            # Display skills as formatted text
            st.text_area("Extracted Skills:", value=skills_text, height=200, disabled=True)
        
        st.divider()
        
        st.subheader("Interview Progress")
        if st.session_state.asked_skills:
            st.write(f"**Skills Evaluated:** {len(st.session_state.asked_skills)}")
            for i, skill in enumerate(st.session_state.asked_skills, 1):
                st.write(f"{i}. {skill}")
    else:
        st.info("Initialize interview to see details.")


# Main content area
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
    # Display chat messages
    st.subheader("Interview Chat")
    
    message_container = st.container()
    
    with message_container:
        # Display all messages
        for msg in st.session_state.messages:
            if msg["role"] == "agent":
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(msg["content"])
                    if "skill" in msg:
                        st.caption(f"📌 Evaluating: {msg['skill']}")
            else:  # user
                with st.chat_message("user", avatar="👤"):
                    st.write(msg["content"])
    
    # Input form and logic
    if not st.session_state.interview_complete:
        # If no messages yet, start the interview
        if not st.session_state.messages:
            st.info("Click the button below to start the first question.")
            if st.button("Get First Question", use_container_width=True):
                with st.spinner("Generating first question..."):
                    start_interview()
                    st.rerun()
        else:
            # Chat input
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
            
            if submit_button and user_input:
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input
                })
                
                # Update agent with the answer
                if st.session_state.agent:
                    st.session_state.agent.asked.append(user_input)
                
                # Get next question
                with st.spinner("Agent thinking..."):
                    decision = st.session_state.agent.decide_next()
                    
                    if decision:
                        try:
                            decision_json = json.loads(decision)
                            
                            if decision_json.get("action") == "stop":
                                st.session_state.interview_complete = True
                                st.session_state.messages.append({
                                    "role": "agent",
                                    "content": "Thank you for the interview! Your responses have been recorded."
                                })
                            else:
                                question = decision_json.get("question", "")
                                skill = decision_json.get("skill", "")
                                if question:
                                    st.session_state.asked_skills.append(skill)
                                    st.session_state.messages.append({
                                        "role": "agent",
                                        "content": question,
                                        "skill": skill
                                    })
                        except json.JSONDecodeError:
                            st.error("Error parsing agent response.")
                
                st.rerun()
    else:
        # Interview complete
        st.success("✅ Interview Complete!")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Start New Interview", use_container_width=True):
                st.session_state.interview_initialized = False
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            if st.button("Download Summary", use_container_width=True):
                # Create summary
                summary = f"""
INTERVIEW SUMMARY
=================

Job Role: {st.session_state.job_info['Title']}
Job Code: {st.session_state.job_info['NCO_Code']}

Skills Evaluated:
{chr(10).join([f"- {skill}" for skill in st.session_state.asked_skills])}

Interview Length: {len(st.session_state.messages)} messages

Interview Transcript:
{chr(10).join([f"{msg['role'].upper()}: {msg['content']}" for msg in st.session_state.messages])}
                """
                st.download_button(
                    label="Download Summary",
                    data=summary,
                    file_name="interview_summary.txt",
                    mime="text/plain"
                )
