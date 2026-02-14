# Running the Interview Agent UI

## Installation

First, install Streamlit if you haven't already:

```bash
pip install streamlit
```

Or add it to your requirements.txt:

```bash
streamlit>=1.28.0
```

## Running the Application

From the project directory, run:

```bash
streamlit run app.py
```

This will:
1. Open a web browser at `http://localhost:8501`
2. Display the interview interface
3. Allow you to start the interview and interact with the agent

## Features

### 🎯 Main Features
- **Resume Display**: View extracted skills from your resume in the sidebar
- **Job Matching**: See the matched job role from the NCO database
- **Interview Chat**: Interactive chat interface for the interview
- **Progress Tracking**: Real-time display of evaluated skills
- **Interview Summary**: Download the complete interview transcript at the end

### 📋 Interface Components

**Left Sidebar:**
- Job role details (title, code, description)
- Extracted skills from resume
- Interview progress (skills evaluated so far)

**Main Area:**
- Chat messages between agent and candidate
- Message bubbles with role indicators
- Input field for typing answers
- Start/Send buttons for interaction

**Interview Flow:**
1. Click "Start Interview" button
2. Click "Get First Question" to receive the first question
3. Read the question and type your answer
4. Click "Send" to submit
5. Agent generates and displays the next question
6. Repeat until interview completes
7. Download summary or start a new interview

## Keyboard Shortcuts

- **Enter**: If using text input form, submit answer
- The "Send" button can also be clicked directly

## Tips

- Each interview session maintains context (asked questions, skills evaluated)
- The sidebar updates in real-time with your interview progress
- The agent decides when to stop based on skill evaluation confidence
- You can start a new interview anytime from the completion screen

## Troubleshooting

If you get an error:
1. Ensure all dependencies are installed (`requirements.txt`)
2. Check that `resumes/resume1.txt` exists
3. Verify that FAISS assets are downloaded
4. Make sure Ollama is running (for LLM inference)

## Command Line (Legacy)

The original command-line interface is still available:

```bash
python main.py
```

But the Streamlit UI is recommended for a better user experience.
