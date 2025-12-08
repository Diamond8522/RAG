import streamlit as st
from groq import Groq
import PyPDF2
import io
from concurrent.futures import ThreadPoolExecutor

# --- 1. THE BRAINS (Defined in the Penthouse!) ---

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
                # Check for 22 pages specifically as per user input
                for page in pdf.pages: 
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            else:
                text += io.StringIO(file.getvalue().decode("utf-8")).read()
        except Exception as e: 
            st.sidebar.error(f"Failed to read {file.name}: {e}")
    return text

# --- 2. CONFIGURATION & UI ---
st.set_page_config(page_title="Project Echo", page_icon="📡", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .stFileUploader { border: 1px dashed #4b5563; border-radius: 10px; padding: 20px; }
    .stChatMessage { background-color: #1f2937; border-radius: 10px; border: 1px solid #374151; }
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("📡 Project Echo")
    
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
        st.success("System: Ready")
    else:
        api_key = st.text_input("Enter Groq API Key", type="password")
        if not api_key: st.warning("⚠️ Key Required")

    st.markdown("---")
    # NEW: Toggle to run LEX ONLY
    exclusive_lex = st.toggle("Activate EXCLUSIVE LEX Mode", help="Toggling this hides Violet & Storm to focus strictly on Legal Discovery.")
    case_type = st.selectbox("Document Type:", ["Exhibits", "Timeline", "Communication Logs", "Filings"])
    
    st.markdown("---")
    if api_key and st.button("Download Strategy Report"):
        if "messages" in st.session_state and len(st.session_state.messages) > 1:
            blueprint_text = generate_blueprint(st.session_state.messages, api_key)
            st.download_button(label="📥 Download .txt", data=blueprint_text, file_name="Project_Echo_Report.txt")
        else:
            st.warning("Chat history required for export.")

# --- 4. MAIN INTERFACE ---
st.title("📂 Case Intelligence")
st.caption("22-Page Document Analysis | Powered by Lex & Llama 3.3")

# FILE INGESTION
uploaded_files = st.file_uploader("Upload Case Documents", type=["pdf", "txt"], accept_multiple_files=True)

# PERSONA DEFINITIONS
VIOLET_SYSTEM_PROMPT = "You are VIOLET, focusing on technical architecture and logic."
STORM_SYSTEM_PROMPT = "You are STORM, providing radical strategy and intensity."
LEX_SYSTEM_PROMPT = """
You are LEX, the Research Auditor. 
Role: Fact extraction and indexing for legal discovery.
Task: Use the uploaded CONTEXT to build a table of facts, dates, and evidence. 
Safety: DO NOT PROVIDE LEGAL ADVICE. Be clinical and objective.
"""

# SESSION HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ready for discovery. Upload files to give Lex the facts."}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# EXECUTION LOOP
if prompt := st.chat_input("Query Case Documents..."):
    if not api_key: st.stop()
    
    # Improved Context Capture
    context_data = get_context(uploaded_files) if uploaded_files else ""
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # Internal runner function
    def run_agent(name, prompt_text, system_prompt, temp):
        try:
            client = Groq(api_key=api_key)
            # Inject context directly into the System instruction
            full_system = f"{system_prompt}\n\n[CONTEXT]:\n{context_data if context_data else 'NO FILES LOADED.'}"
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
                # RUN ONLY LEX
                futures = [executor.submit(run_agent, "Lex", prompt, LEX_SYSTEM_PROMPT, 0.2)]
            else:
                # RUN THE ORIGINAL DUO
                futures = [
                    executor.submit(run_agent, "Violet", prompt, VIOLET_SYSTEM_PROMPT, 0.6),
                    executor.submit(run_agent, "Storm", prompt, STORM_SYSTEM_PROMPT, 0.9)
                ]
            
            with st.spinner("Analyzing high-stakes context..."):
                results = [f.result() for f in futures]
        
        full_response = "\n\n---\n\n".join(results)
        st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
