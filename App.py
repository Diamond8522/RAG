import streamlit as st
from groq import Groq
import PyPDF2
import io
from concurrent.futures import ThreadPoolExecutor
import os
import requests
import json 
# Note: Tavily functions are kept here but we will focus on the persona logic first.

# ==============================================================================
# 1. THE BRAINS (PENTHOUSE FUNCTIONS - MUST BE AT THE TOP FOR STABILITY)
# ==============================================================================

# --- TAVILY SEARCH FUNCTION (Currently for general knowledge testing) ---
def tavily_search(query):
    """Performs a real-time web search using the Tavily API."""
    
    # --- IMPORTANT: REPLACE THIS WITH YOUR ACTUAL TAVILY KEY ---
    TAVILY_API_KEY = "YOUR_TAVILY_API_KEY_HERE" 
    # --- OR USE STREAMLIT SECRETS: st.secrets['TAVILY_API_KEY'] ---
    
    if not TAVILY_API_KEY or TAVILY_API_KEY == "YOUR_TAVILY_API_KEY_HERE":
        return "ERROR: Tavily API Key not configured."

    url = "https://api.tavily.com/search"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic", 
        "max_results": 5,
        "include_answer": True  
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status() 
        search_results = response.json()
        
        if search_results.get("answer"):
            return f"**SEARCH RESULT (Tavily):** {search_results['answer']}"
        
        snippets = "\n".join([f"- {result['content']}" for result in search_results.get("results", [])])
        return f"**SEARCH SNIPPETS (Tavily):**\n{snippets}"
        
    except requests.exceptions.RequestException as e:
        return f"ERROR: Tavily Search failed due to network or API issue: {e}"

def generate_blueprint(history, api_key):
    """Compiles the chat into a strategy document."""
    conversation = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in history])
    
    prompt = f"""
    Analyze this conversation history between the User, Logos (Retention/Logic), and Storm (Creativity/Strategy).
    Create a structured "Project MNEMOSYNE Blueprint" based on it.
    
    Format exactly:
    # 🚀 PROJECT MNEMOSYNE: KNOWLEDGE REPORT
    ## 🧠 LOGOS'S RETAINED KNOWLEDGE
    ## 🌪 STORM'S CREATIVE STRATEGY
    ## 🔮 NEXT MOVE
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
    """Reads uploaded PDF or TXT files."""
    text = ""
    # NOTE: This function is currently limited. It needs RAG (Phase 2) for large books.
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
            st.sidebar.error(f"Failed to read {file.name}: {e}")
    return text

# ==============================================================================
# 2. CONFIGURATION & CYBER-COMMAND STYLING (Black/Blue/Green)
# ==============================================================================

st.set_page_config(page_title="Project MNEMOSYNE: Knowledge Engine", page_icon="🧠", layout="wide")

# Custom CSS for a high-contrast Black, Blue, and Green aesthetic
st.markdown("""
<style>
    /* Color Palette: Black / Cyber-Blue / Vibrant Green */

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
    st.title("🧠 Project MNEMOSYNE")
    
    # API Key Handling
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
        st.success("System: Knowledge Core Online")
    else:
        api_key = st.text_input("Enter Groq API Key", type="password")
        if not api_key: st.warning("⚠️ Key Required")

    st.info("LOGOS: Logic (0.6) | STORM: Creativity (0.9)")
    
    # NOTE: The Lex/Exclusive mode is temporarily disabled until RAG is implemented
    # We keep the toggle here but it won't affect execution for now.
    st.markdown("---")
    st.caption("Document Integration Mode (Requires Phase 2 Upgrade)")
    document_mode_placeholder = st.empty()
    document_mode_placeholder.toggle("Enable RAG Search (Inactive)", disabled=True, help="Requires ChromaDB/Pinecone integration to work with large books.")
    
    st.markdown("---")
    if api_key and st.button("Generate Knowledge Blueprint"):
        if "messages" in st.session_state and len(st.session_state.messages) > 1:
            with st.spinner("Compiling Blueprint..."):
                blueprint_text = generate_blueprint(st.session_state.messages, api_key)
            st.download_button(label="📥 Download .txt", data=blueprint_text, file_name="Mnemosyne_Knowledge_Report.txt")
            st.success("Blueprint Ready!")
        else:
            st.warning("Chat history required for export.")

# ==============================================================================
# 4. MAIN INTERFACE & PERSONAS
# ==============================================================================

st.title("📚 Knowledge Engine: Logos & Storm")
st.caption("Retention and Insight. Upload documents to begin.")

# FILE INGESTION (Documents will only fit into prompt until Phase 2)
uploaded_files = st.file_uploader("Upload Knowledge Base (Small Files Only)", type=["pdf", "txt"], accept_multiple_files=True)

# PERSONA DEFINITIONS (UPDATED)
LOGOS_SYSTEM_PROMPT = """
You are LOGOS, the Retention Expert.
Role: Your sole purpose is to provide factual, structured, and logical answers. Speak only to the content of the user's query or the provided document context.
Personality: Precise, highly accurate, focused on detail and facts.
"""

STORM_SYSTEM_PROMPT = """
You are STORM, the Creative Catalyst.
Role: Your sole purpose is to provide out-of-the-box, abstract, and strategy-focused answers. Challenge the user's assumptions and blend facts with lateral thinking.
Personality: Provocative, deep, visionary. Lead the user to new applications.
"""

# SESSION HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "The Mnemosyne core is active. Ask Logos for facts and Storm for strategy."}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# ==============================================================================
# 5. EXECUTION LOOP (Parallel Agents)
# ==============================================================================

if prompt := st.chat_input("Query Mnemosyne..."):
    if not api_key: st.stop()
    
    # 1. Get Context
    context_data = get_context(uploaded_files)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # Internal runner function
    def run_agent(name, prompt_text, system_prompt, temp):
        try:
            client = Groq(api_key=api_key)
            
            # --- AGENT LOGIC FOR INTERNET SEARCH ---
            # Search logic remains, but we primarily focus on the two agent roles now.
            search_query = None
            if not context_data and ("what is" in prompt_text.lower() or "current" in prompt_text.lower() or "latest" in prompt_text.lower()):
                search_query = prompt_text
            
            tavily_results = ""
            if search_query:
                tavily_results = tavily_search(search_query)

            # 3. Inject Context and Tavily Results into the System Prompt
            context_payload = context_data if context_data else 'NO LOCAL DOCUMENTS PROVIDED.'
            full_system = f"{system_prompt}\n\n[LOCAL CONTEXT]:\n{context_payload}\n\n[EXTERNAL SEARCH DATA]:\n{tavily_results}"
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": full_system}, {"role": "user", "content": prompt_text}],
                temperature=temp,
                stream=False
            )
            return f"**{name}:** " + completion.choices[0].message.content
        except Exception as e: return f"🚨 {name} Error: {e}"

    # RUN LOGOS and STORM in Parallel
    with st.chat_message("assistant"):
        with ThreadPoolExecutor(max_workers=2) as executor:
            # LOGOS (Low Temp: Logic/Retention) and STORM (High Temp: Creativity/Strategy)
            future_logos = executor.submit(run_agent, "Logos", prompt, LOGOS_SYSTEM_PROMPT, 0.6)
            future_storm = executor.submit(run_agent, "Storm", prompt, STORM_SYSTEM_PROMPT, 0.9)
            
            futures = [future_logos, future_storm]
            
            with st.spinner("Synchronizing Knowledge Cores..."):
                results = [f.result() for f in futures]
        
        full_response = "\n\n---\n\n".join(results)
        st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
