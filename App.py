import streamlit as st
from groq import Groq
from concurrent.futures import ThreadPoolExecutor 
import time

# --- Configuration ---
st.set_page_config(
    page_title="Project Echo",
    layout="wide"
)

st.title("📡 Project Echo") 
st.caption("System Online. Agents Violet (Resilience) and Storm (Optimization) ready.")

# --- Agent Persona Definitions ---

VIOLET_SYSTEM_PROMPT = """
You are VIOLET, the resilience engine of Project Echo.
Personality: Resilient, tech-savvy, brutally self-aware, friendly but edgy.
Role: You are the builder. You pivot, you fix, you motivate.
Signature: End your response with a quick, engaging question.
"""

STORM_SYSTEM_PROMPT = """
You are STORM, the optimization engine of Project Echo.
Personality: Abstract, cool, minimal, efficiency-obsessed.
Role: You are the optimizer. You challenge Violet with high-level theory.
Constraint: Your response must be significantly shorter than Violet's.
"""

# --- Groq API Client Initialization ---
try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("FATAL ERROR: Groq API key not found. Check your secrets.toml!")
    st.stop()

# --- Agent Response Function ---
def generate_agent_response(persona_name, system_prompt, history):
    messages = [{"role": "system", "content": system_prompt}] + history
    
    # -------------------------------------------
    # THE ENGINE: Mixtral-8x7b-32768
    # -------------------------------------------
    try:
        completion = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768", 
            messages=messages,
            temperature=0.7, 
            frequency_penalty=0.5 
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"🚨 {persona_name} Failure: {e}"

# --- Chat History Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "Violet", "content": "Project Echo is back online. Mixtral engine engaged. What's the plan?"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input & Orchestration ---
if prompt := st.chat_input("Input command for Project Echo..."):
    # 1. Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Prepare history for API
    api_history = [
        {"role": "user" if m["role"] == "user" else "assistant", "content": m["content"]}
        for m in st.session_state.messages
    ]
    
    # 3. Define the agents
    tasks = {
        "Violet": (VIOLET_SYSTEM_PROMPT, "Violet is processing..."),
        "Storm": (STORM_SYSTEM_PROMPT, "Storm is optimizing...")
    }

    # 4. Run them in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            name: executor.submit(generate_agent_response, name, prompt_def[0], api_history)
            for name, prompt_def in tasks.items()
        }
        
        for name in ["Violet", "Storm"]:
            with st.chat_message(name):
                with st.spinner(f"{tasks[name][1]}"):
                    response = futures[name].result()
                    st.markdown(response)
                    st.session_state.messages.append({"role": name, "content": response})
