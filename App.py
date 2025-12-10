import streamlit as st
from groq import Groq
import PyPDF2
import io
from concurrent.futures import ThreadPoolExecutor

# ==============================================================================
# 1. THE BRAINS (PENTHOUSE FUNCTIONS - MUST BE AT THE TOP FOR STABILITY)
# ==============================================================================

def generate_blueprint(history, api_key):
    """Compiles the chat into a strategy document."""
    conversation = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in history])
    
    prompt = f"""
    Analyze this conversation history between the User and the active Agents.
    Create a structured "Project Blueprint" based on it.
    
    Format exactly:
    # 🚀 PROJECT ECHO: STRATEGY REPORT
    ## 🛠 PLAN/FACT AUDIT
    ## 🔮 NEXT MOVES
    === CHAT LOG ===
    {conversation}
    """
    
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error generating blueprint: {e}"

def get_context(files):
    """Reads uploaded PDF or TXT files with improved error feedback."""
    text = ""
    for file in files:
        try:
            if file.type == "application/pdf":
                pdf = PyPDF2.PdfReader(file)
                for page in pdf.pages: 
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            else:
                text += io.StringIO(file.getvalue().decode("utf-8")).read()
        except Exception as e: 
            # Use st.sidebar.error to show file reading failure without crashing the app
            st.sidebar.error(f"Failed to read {file.name}: {e}")
    return text

# ==============================================================================
# 2. CONFIGURATION & CYBER-COMMAND STYLING (Black/Blue/Green)
# ==============================================================================

st.set_page_config(page_title="Project Echo: Cyber-Command Logic", page_icon="📡", layout="wide")

# Custom CSS for a high-contrast Black, Blue, and Green aesthetic
st.markdown("""
<style>
    /* Color Palette: 
       Background: #000000 (Black)
       Primary Text/Accent: #00FFFF (Bright Cyber-Blue)
       Secondary Accent/Success: #00FF00 (Vibrant Green)
    */

    /* 1. Overall App Background (Deep Black) */
    .stApp {
        background-color: #000000;
        color: #00FFFF; /* Default text color is bright Cyber-Blue */
        font-family: 'Consolas', 'Courier New', monospace;
    }

    /* 2. Sidebar Look (Slightly lighter black for contrast) */
    .stSidebar {
        background-color: #0A0A0A; 
        border-right: 2px solid #00FF00; /* Vibrant Green divider */
        color: #00FFFF;
    }

    /* 3. Chat Message Containers (Blue border on black background) */
    .stChatMessage {
        background-color: #1A1A1A; 
        border: 1px solid #00FFFF; /* Cyber-Blue border */
        border-radius: 4px;
        padding: 10px;
        margin-bottom: 10px;
    }

    /* 4. Headings and Titles (Command Center Blue) */
    h1, h2, h3, .css-1d3fpjk { 
        color: #00FFFF; 
        border-bottom: 2px dashed #00FF00; /* Green dashed line */
        padding-bottom: 5px;
        margin-top: 15px;
    }
    
    /* 5. Input Area and Buttons (Green accents) */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > button,
    .stFileUploader {
        background-color: #222222;
        color: #00FFFF; 
        border: 2px solid #00FF00; /* Vibrant Green Input Border */
        border-radius: 4px;
    }
    .stButton > button {
        background-color: #004400; /* Dark Green button background */
        color: #00FF00; /* Green text */
        border: 2px solid #00FFFF; /* Blue outer border */
        font-weight: bold;
        transition: background-color 0.2s;
    }
    .stButton > button:hover {
        background-color: #005500; 
        box-shadow: 0 0 5px #00FFFF; /* Blue glow on hover */
    }
    
    /* 6. Success/Error Messages (Should pop) */
    .stSuccess {
        background-color: #00FF00 !important; /* Bright Green Success */
        color: #000000 !important;
        border: 1px solid #00FFFF !important;
    }
    .stWarning, .stError {
        background-color: #FF0000 !important; /* Bright Red Error/Warning */
        color: #00FFFF !important;
    }

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. SIDEBAR CONTROLS
# ==============================================================================

with st.sidebar:
    st.title("📡 Project Echo")
    
    # API Key Handling
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
        st.success("System: Ready")
    else:
        api_key = st.text_input("Enter Groq API Key", type="password")
        if not api_key: st.warning("⚠️ Key Required")

    st.markdown("---")
    # LEX EXCLUSIVE MODE TOGGLE
    exclusive_lex = st.toggle("Activate EXCLUSIVE LEX Mode", help="Toggling this hides Violet & Storm to focus strictly on Legal Discovery (LEX only).")
    case_type = st.selectbox("Document Type:", ["Exhibits", "Timeline", "Communication Logs", "Filings"])
    
    st.markdown("---")
    if api_key and st.button("Download Strategy Report"):
        if "messages" in st.session_state and len(st.session_state.messages) > 1:
            with st.spinner("Compiling Blueprint..."):
                blueprint_text = generate_blueprint(st.session_state.messages, api_key)
            st.download_button(label="📥 Download .txt", data=blueprint_text, file_name="Project_Echo_Report.txt")
            st.success("Blueprint Ready!")
        else:
            st.warning("Chat history required for export.")

# ==============================================================================
# 4. MAIN INTERFACE & PERSONAS
# ==============================================================================

st.title("📂 Case Intelligence")
st.caption("22-Page Document Analysis | Powered by Lex & Llama 3.3")

# FILE INGESTION
uploaded_files = st.file_uploader("Upload Case Documents", type=["pdf", "txt"], accept_multiple_files=True)

# PERSONA DEFINITIONS
VIOLET_SYSTEM_PROMPT = """
You are VIOLET, the Architect.
Role: Technical step-by-step foundation and logic.
Personality: Resilient, clear, practical.
"""

STORM_SYSTEM_PROMPT = """
You are STORM, the Agent of Intensity.
Role: Radical Visionary thinking OUTSIDE THE BOX.
Personality: Direct, deep, abstract. Connect the dots the user doesn't see.
"""

LEX_SYSTEM_PROMPT = """
You are LEX, the Research Auditor. 
Role: Document indexing and fact extraction for legal discovery.
Task: Use the uploaded CONTEXT to build a table of facts, dates, and evidence. 
Safety: DO NOT PROVIDE LEGAL ADVICE. Be clinical and objective.
"""

# SESSION HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ready for discovery. Upload files to give Lex the facts."}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# ==============================================================================
# 5. EXECUTION LOOP (Parallel Agents)
# ==============================================================================

if prompt := st.chat_input("Query Case Documents..."):
    if not api_key: st.stop()
    
    # 1. Get Context
    context_data = get_context(uploaded_files)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # Internal runner function
    def run_agent(name, prompt_text, system_prompt, temp):
        try:
            client = Groq(api_key=api_key)
            # Inject context directly into the System instruction
            context_payload = context_data if context_data else 'NO FILES LOADED. ASK THE USER TO UPLOAD.'
            full_system = f"{system_prompt}\n\n[CONTEXT]:\n{context_payload}"
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": full_system}, {"role": "user", "content": prompt_text}],
                temperature=temp,
                stream=False
            )
            return f"**{name}:** " + completion.choices[0].message.content
        except Exception as e: return f"🚨 {name} Error: {e}"

    # THE PIVOT: Exclusive Logic
    with st.chat_message("assistant"):
        with ThreadPoolExecutor(max_workers=3) as executor:
            if exclusive_lex:
                # RUN ONLY LEX (Low Temp for accuracy)
                futures = [executor.submit(run_agent, "Lex", f"[AUDIT TYPE: {case_type}] {prompt}", LEX_SYSTEM_PROMPT, 0.2)]
            else:
                # RUN THE ORIGINAL DUO (Violet/Storm)
                futures = [
                    executor.submit(run_agent, "Violet", prompt, VIOLET_SYSTEM_PROMPT, 0.6),
                    executor.submit(run_agent, "Storm", prompt, STORM_SYSTEM_PROMPT, 0.9)
                ]
            
            with st.spinner("Synchronizing Agents..."):
                results = [f.result() for f in futures]
        
        full_response = "\n\n---\n\n".join(results)
        st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
