# NCO-Agent: Resume-Aware Interview Agent using Semantic Job Matching

An agentic AI system that grounds automated interviews in government NCO job codes using FAISS-based semantic search and an LLM-driven adaptive interview agent.

The system:
- Semantically matches free-text job intent to official NCO job roles
- Extracts skills from resumes
- Uses a stateful LLM agent to decide interview questions dynamically
- Runs fully locally using Ollama (no cloud APIs)

--------------------------------------------------------------------

HIGH-LEVEL ARCHITECTURE

Resume (text/pdf)
   ↓
Skill Extraction
   ↓
Semantic Job Matching (SBERT + FAISS over NCO data)
   ↓
Canonical Job Role (Title + Code + Description)
   ↓
Agentic Interview Loop (LLM via Ollama)

--------------------------------------------------------------------
REQUIREMENTS

System:
- macOS (Apple Silicon or Intel)
- Python 3.9 / 3.10 / 3.11 (Python 3.12 NOT supported by FAISS yet)
- Git
- Ollama (local LLM runtime)

Python Libraries:
- faiss-cpu
- sentence-transformers
- numpy < 2.0
- pandas
- ollama (Python client)
--------------------------------------------------------------------
SETUP INSTRUCTIONS

1) Clone and Setup Environment
   
```bash
git clone https://github.com/your-username/nco-agentic-interview.git
cd nco-agentic-interview
python3.9 -m venv venv
source venv/bin/activate
```
--------------------------------------------------------------------
3) Install dependencies (IMPORTANT: NumPy version)

Upgrade pip:
```bash
pip install --upgrade pip
```
Install NumPy compatible with FAISS:
```bash
pip install "numpy<2"
```
Install remaining dependencies:
```bash
pip install faiss-cpu==1.7.4 sentence-transformers pandas ollama
```
--------------------------------------------------------------------
4) Install and start Ollama

Install Ollama (one-time):
https://ollama.com

Pull the model:
```bash
ollama pull llama3.1:8b
```
Start Ollama (every session):
```bash
open -a Ollama
```
Verify Ollama is running:
```bash
ollama list
```
--------------------------------------------------------------------
5) Ensure FAISS assets are present

Place the following files inside faiss_assets/:

- nco_faiss.index
- index_df_canonical.csv
- sbert_nco_finetuned/

These assets are generated from the NCO dataset preprocessing pipeline.
--------------------------------------------------------------------
6) Run the system
```bash
python main.py
```
Expected flow:
- Resume is loaded
- Top NCO job match is printed
- Agent asks an interview question
- User answers in the terminal
--------------------------------------------------------------------

DAILY USAGE (AFTER SETUP)

Every new session:
```bash
cd nco-agentic-interview
source venv/bin/activate
open -a Ollama
python main.py
```
--------------------------------------------------------------------
COMMON ISSUES

FAISS import error:
- Ensure venv is active
- Ensure NumPy version < 2.0
- Reinstall if needed:
```bash
pip uninstall numpy -y
pip install "numpy<2"
pip install faiss-cpu==1.7.4
```
--------------------------------------------------------------------
Ollama connection error:
- Ensure Ollama app is running
- Check with:
  
```bash
ollama list
```

NOTES

- FAISS is used strictly for job grounding, not generation
- LLM is used for decision-making, not free chat
- Interview agent maintains internal state
- System is modular and extensible

AUTHOR

Adithya
