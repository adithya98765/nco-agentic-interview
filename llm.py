# llm.py
import ollama
import json
import re

def ask_llm(system_prompt, user_prompt):
    response = ollama.chat(
        model="phi3:mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    content = response["message"]["content"]
    
    # Try to extract JSON if wrapped in code blocks
    if "```" in content:
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
    
    # Try to find JSON object in the response
    brace_start = content.find("{")
    brace_end = content.rfind("}")
    if brace_start != -1 and brace_end != -1:
        content = content[brace_start:brace_end+1]
    
    return content.strip()

