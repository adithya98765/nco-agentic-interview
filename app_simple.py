import streamlit as st
import json

# Set page config first
st.set_page_config(
    page_title="NCO Interview Agent",
    page_icon="",
    layout="wide"
)

st.title("🎤 NCO Interview Agent")

# Try to import dependencies
try:
    from resume_parser import extract_skills
    from faiss_search import NCOSemanticSearch
    from agent import InterviewAgent
    imports_ok = True
except Exception as e:
    imports_ok = False
    st.error(f"❌ Import Error: {str(e)}")
    st.info("Make sure all dependencies are installed: `pip install -r requirements.txt`")
    st.stop()

# Initialize session state
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.agent = None
    st.session_state.job_info = None
    st.session_state.skills = None
    st.session_state.messages = []
    st.session_state.done = False

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
            with st.spinner("Initializing..."):
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
        if st.button("Get First Question"):
            try:
                with st.spinner("Generating question..."):
                    decision = st.session_state.agent.decide_next()
                    
                    # Clean up the response - remove markdown code blocks if present
                    decision = decision.strip()
                    if decision.startswith("```"):
                        decision = decision.split("```")[1]
                        if decision.startswith("json"):
                            decision = decision[4:]
                        decision = decision.strip()
                    
                    st.write(f"Debug - Raw response: {decision[:100]}...")  # Show first 100 chars
                    
                    decision_json = json.loads(decision)
                    st.write(f"Debug - Parsed JSON: {decision_json}")
                    
                    if decision_json.get("action") == "stop":
                        st.session_state.done = True
                        st.info("Interview stopped by agent")
                    else:
                        question = decision_json.get("question", "No question provided")
                        st.session_state.messages.append({
                            "role": "agent",
                            "content": question
                        })
                    st.rerun()
            except json.JSONDecodeError as e:
                st.error(f"❌ JSON Parse Error: {str(e)}")
                st.write("Raw response was:", decision[:200])
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                st.write(traceback.format_exc())
    
    # Answer input
    if not st.session_state.done and st.session_state.messages:
        answer = st.text_input("Your answer:", key="answer_input")
        if answer and st.button("Send"):
            try:
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": answer
                })
                
                # Update agent
                st.session_state.agent.asked.append(answer)
                
                # Get next question
                with st.spinner("Agent thinking..."):
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
                            "content": "✅ Interview Complete! Thank you!"
                        })
                        st.session_state.done = True
                    else:
                        question = decision_json.get("question", "No question")
                        st.session_state.messages.append({
                            "role": "agent",
                            "content": question
                        })
                
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Restart button
    if st.session_state.done:
        st.success("Interview Completed!")
        if st.button("Start New Interview"):
            st.session_state.started = False
            st.session_state.messages = []
            st.session_state.done = False
            st.rerun()
