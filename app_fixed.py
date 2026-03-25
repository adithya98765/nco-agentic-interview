import streamlit as st
import json
import time

# Set page config first
st.set_page_config(
    page_title="NCO Interview Agent",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 NCO Interview Agent")

# Try to import dependencies
try:
    from resume_parser import extract_skills
    from faiss_search import NCOSemanticSearch
    from agent import InterviewAgent
except Exception as e:
    st.error(f"❌ Import Error: {str(e)}")
    st.stop()

# Initialize session state
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.agent = None
    st.session_state.job_info = None
    st.session_state.skills = None
    st.session_state.messages = []
    st.session_state.done = False
    st.session_state.loading = False

# Main app logic
if not st.session_state.started:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("""
        Welcome! This system will:
        - Analyze your resume
        - Find matching job roles
        - Conduct an interview
        """)
    
    with col2:
        if st.button("🚀 Start Interview", use_container_width=True, type="primary"):
            try:
                # Load resume
                with open("resumes/resume1.txt") as f:
                    resume_text = f.read()
                st.session_state.skills = extract_skills(resume_text)
                
                # Search for job
                searcher = NCOSemanticSearch()
                jobs = searcher.search("software engineer", k=1)
                st.session_state.job_info = jobs[0]
                
                # Create agent
                st.session_state.agent = InterviewAgent(
                    job_info=st.session_state.job_info,
                    resume_skills=st.session_state.skills
                )
                
                st.session_state.started = True
                st.rerun()
            except FileNotFoundError as e:
                st.error(f"❌ File not found: {str(e)}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.write(str(e))

else:
    # Show job info
    with st.sidebar:
        st.subheader("📋 Job Info")
        st.write(f"**{st.session_state.job_info['Title']}**")
        st.write(f"Code: {st.session_state.job_info['NCO_Code']}")
    
    # Chat interface
    st.subheader("Interview")
    
    # Display messages
    for msg in st.session_state.messages:
        if msg["role"] == "agent":
            with st.chat_message("assistant"):
                st.write(msg["content"])
        else:
            with st.chat_message("user"):
                st.write(msg["content"])
    
    # Get first question if needed
    if not st.session_state.messages and not st.session_state.done:
        st.info("Click the button below to get your first question.")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Get First Question", use_container_width=True, key="first_q_btn"):
                st.session_state.loading = True
                st.rerun()
    
    # Process first question if loading
    if st.session_state.loading and not st.session_state.messages:
        with st.spinner("Generating first question... This may take a moment."):
            try:
                decision = st.session_state.agent.decide_next()
                
                # Clean up the response
                decision = decision.strip()
                if decision.startswith("```"):
                    decision = decision.split("```")[1]
                    if decision.startswith("json"):
                        decision = decision[4:]
                    decision = decision.strip()
                
                decision_json = json.loads(decision)
                
                if decision_json.get("action") == "stop":
                    st.session_state.done = True
                    st.session_state.messages.append({
                        "role": "agent",
                        "content": "Interview ended."
                    })
                else:
                    question = decision_json.get("question", "No question provided")
                    st.session_state.messages.append({
                        "role": "agent",
                        "content": question
                    })
                
                st.session_state.loading = False
                st.rerun()
                
            except json.JSONDecodeError as e:
                st.error(f"JSON Parse Error: {str(e)}")
                st.write("Response:", decision[:200] if 'decision' in locals() else "No response")
                st.session_state.loading = False
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.loading = False
    
    # Answer input
    if not st.session_state.done and st.session_state.messages and not st.session_state.loading:
        col1, col2 = st.columns([0.85, 0.15], gap="small")
        
        with col1:
            answer = st.text_input(
                "Your answer:",
                placeholder="Type your response here...",
                label_visibility="collapsed",
                key="answer_input"
            )
        
        with col2:
            send_clicked = st.button("Send", use_container_width=True)
        
        if send_clicked and answer:
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": answer
            })
            
            # Update agent
            st.session_state.agent.asked.append(answer)
            
            st.session_state.loading = True
            st.rerun()
    
    # Process next question if loading after answer
    if st.session_state.loading and len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
        with st.spinner("Agent is thinking..."):
            try:
                decision = st.session_state.agent.decide_next()
                
                # Clean up the response
                decision = decision.strip()
                if decision.startswith("```"):
                    decision = decision.split("```")[1]
                    if decision.startswith("json"):
                        decision = decision[4:]
                    decision = decision.strip()
                
                decision_json = json.loads(decision)
                
                if decision_json.get("action") == "stop":
                    st.session_state.messages.append({
                        "role": "agent",
                        "content": "✅ Interview Complete! Thank you for your responses."
                    })
                    st.session_state.done = True
                else:
                    question = decision_json.get("question", "No question")
                    st.session_state.messages.append({
                        "role": "agent",
                        "content": question
                    })
                
                st.session_state.loading = False
                st.rerun()
                
            except Exception as e:
                st.error(f"Error getting next question: {str(e)}")
                st.session_state.loading = False
    
    # Restart button
    if st.session_state.done:
        st.divider()
        st.success("Interview Completed!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start New Interview", use_container_width=True):
                st.session_state.started = False
                st.session_state.messages = []
                st.session_state.done = False
                st.session_state.loading = False
                st.rerun()
        
        with col2:
            # Export transcript
            summary = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in st.session_state.messages])
            st.download_button(
                label="Download Transcript",
                data=summary,
                file_name="interview_transcript.txt",
                mime="text/plain"
            )
