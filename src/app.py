"""
app.py — Professional dark dashboard edition
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from src.agent import build_agent, run_agent

st.set_page_config(
    page_title="CyberRAG",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

OLLAMA_MODELS = ["llama3.2"]

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

SUGGESTED = [
    "What is a zero-day vulnerability?",
    "How does a phishing attack work?",
    "Explain ransomware and how to prevent it.",
    "What is end-to-end encryption?",
    "How does SQL injection work?",
    "What is a man-in-the-middle attack?",
]

STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

:root {
  --bg:         #0b0f17;
  --bg2:        #0d1219;
  --surface:    #131a24;
  --surface2:   #19212e;
  --surface3:   #1f2836;
  --surface4:   #243040;
  --border:     #253044;
  --border2:    #2e3d55;
  --accent:     #3b82f6;
  --accent-dim: #1d4ed8;
  --accent-bg:  rgba(59,130,246,.08);
  --accent-bd:  rgba(59,130,246,.22);
  --accent-glow:rgba(59,130,246,.15);
  --green:      #34d399;
  --green-bg:   rgba(52,211,153,.08);
  --green-bd:   rgba(52,211,153,.22);
  --orange:     #fb923c;
  --orange-bg:  rgba(251,146,60,.08);
  --text:       #e2e8f0;
  --text2:      #7d90a8;
  --text3:      #3d5068;
  --sans:       'Plus Jakarta Sans', sans-serif;
  --mono:       'Fira Code', monospace;
  --r:          10px;
  --r-sm:       6px;
}

* { box-sizing: border-box; margin: 0; }

/* ── App shell ─────────────────────────────────────────── */
.stApp {
  background:
    radial-gradient(ellipse 70% 50% at 15% 0%, rgba(59,130,246,.06) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 85% 100%, rgba(52,211,153,.04) 0%, transparent 50%),
    var(--bg);
  font-family: var(--sans);
}

[data-testid="stMain"],
[data-testid="stAppViewContainer"] { background: transparent !important; }

.main .block-container {
  padding: 1.75rem 3rem 7rem;
  max-width: 880px;
}

#MainMenu, footer { visibility: hidden; }

/* Make the header transparent but keep it in the DOM so the sidebar toggle still works */
[data-testid="stHeader"] {
  background:    transparent !important;
  border-bottom: none !important;
}
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
  display: none !important;
}

/* ── Sidebar ───────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background:  var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
  overflow-y:    auto !important;
  height:        100vh !important;
  padding-top:   0 !important;
  padding-bottom: 2rem !important;
}
[data-testid="stSidebar"] > div:first-child > div:first-child {
  padding-top: 0 !important;
  margin-top:  0 !important;
}

[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] {
  display: none !important;
}

[data-testid="stSidebar"] label p,
[data-testid="stWidgetLabel"] p {
  font-family:    var(--sans) !important;
  font-size:      .7rem !important;
  font-weight:    700 !important;
  text-transform: uppercase !important;
  letter-spacing: .08em !important;
  color:          var(--text3) !important;
}

/* ── Selectbox ─────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
  background:    var(--surface2) !important;
  border:        1px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  color:         var(--text) !important;
  font-family:   var(--sans) !important;
  font-size:     .875rem !important;
  font-weight:   500 !important;
}
[data-testid="stSelectbox"] > div > div:focus-within {
  border-color: var(--accent) !important;
  box-shadow:   0 0 0 3px var(--accent-bg) !important;
}

/* ── Buttons ───────────────────────────────────────────── */
.stButton button {
  background:    var(--surface2) !important;
  color:         var(--text2) !important;
  border:        1px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  font-family:   var(--sans) !important;
  font-size:     .8125rem !important;
  font-weight:   500 !important;
  letter-spacing: .01em !important;
  transition:    all .15s ease !important;
  padding:       .45rem 1rem !important;
}
.stButton button:hover {
  background:    var(--surface3) !important;
  border-color:  var(--border2) !important;
  color:         var(--text) !important;
  transform:     translateY(-1px) !important;
  box-shadow:    0 4px 12px rgba(0,0,0,.3) !important;
}

/* ── Chat messages ─────────────────────────────────────── */
[data-testid="stChatMessage"] {
  background:    transparent !important;
  border:        none !important;
  border-radius: 0 !important;
  padding:       1.25rem 0 !important;
  margin-bottom: 0 !important;
  position:      relative;
  animation:     msgIn .25s ease both;
}

/* Separator between messages */
[data-testid="stChatMessage"] + [data-testid="stChatMessage"] {
  border-top: 1px solid var(--border) !important;
}

/* ── Assistant message ────────────────────────────────── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
  background:    transparent !important;
}

/* ── User message ─────────────────────────────────────── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  background:    var(--surface2) !important;
  border:        1px solid var(--border) !important;
  border-radius: var(--r) !important;
  padding:       1.1rem 1.25rem !important;
  margin:        .5rem 0 !important;
  box-shadow:    0 1px 3px rgba(0,0,0,.2) !important;
}

/* ── Message text ─────────────────────────────────────── */
[data-testid="stChatMessage"] .stMarkdown p {
  font-family: var(--sans) !important;
  font-size:   .9375rem !important;
  color:       var(--text) !important;
  line-height: 1.8 !important;
}
[data-testid="stChatMessage"] .stMarkdown p + p {
  margin-top: .8rem !important;
}
[data-testid="stChatMessage"] .stMarkdown strong {
  color:       var(--text) !important;
  font-weight: 600 !important;
}
[data-testid="stChatMessage"] .stMarkdown em {
  color: var(--text2) !important;
}
[data-testid="stChatMessage"] .stMarkdown h3,
[data-testid="stChatMessage"] .stMarkdown h4 {
  color:       var(--text) !important;
  font-size:   1rem !important;
  font-weight: 600 !important;
  margin:      1rem 0 .4rem !important;
}
[data-testid="stChatMessage"] .stMarkdown ul,
[data-testid="stChatMessage"] .stMarkdown ol {
  padding-left: 1.35rem !important;
  margin:       .6rem 0 !important;
}
[data-testid="stChatMessage"] .stMarkdown li {
  color:       var(--text) !important;
  font-size:   .9375rem !important;
  line-height: 1.8 !important;
  margin:      .2rem 0 !important;
}
[data-testid="stChatMessage"] .stMarkdown li::marker {
  color: var(--text3) !important;
}

/* Inline code */
[data-testid="stChatMessage"] .stMarkdown code {
  background:    var(--surface3) !important;
  color:         var(--accent) !important;
  border:        1px solid var(--border) !important;
  font-family:   var(--mono) !important;
  font-size:     .8125rem !important;
  border-radius: var(--r-sm) !important;
  padding:       .12em .45em !important;
  font-weight:   500 !important;
}

/* Code blocks */
[data-testid="stChatMessage"] .stMarkdown pre {
  background:    var(--surface2) !important;
  border:        1px solid var(--border) !important;
  border-top:    3px solid var(--accent) !important;
  border-radius: var(--r) !important;
  padding:       1.1rem 1.25rem !important;
  overflow-x:    auto !important;
  margin:        .75rem 0 !important;
}
[data-testid="stChatMessage"] .stMarkdown pre code {
  background: transparent !important;
  border:     none !important;
  color:      var(--text) !important;
  font-size:  .8125rem !important;
  padding:    0 !important;
}

/* Blockquote as citation */
[data-testid="stChatMessage"] .stMarkdown blockquote {
  border-left:  3px solid var(--accent) !important;
  padding-left: .9rem !important;
  color:        var(--text2) !important;
  font-style:   italic !important;
  margin:       .75rem 0 !important;
}

/* ── Avatar ────────────────────────────────────────────── */
[data-testid="chatAvatarIcon-assistant"] {
  background:    var(--accent-bg) !important;
  border:        1px solid var(--accent-bd) !important;
  border-radius: var(--r-sm) !important;
}
[data-testid="chatAvatarIcon-user"] {
  background:    var(--surface3) !important;
  border:        1px solid var(--border2) !important;
  border-radius: var(--r-sm) !important;
}

/* ── Chat input area ───────────────────────────────────── */
.stChatInputContainer,
.stChatInputContainer > div,
.stChatInputContainer > div > div {
  background: var(--bg) !important;
  border:     none !important;
}
.stChatInputContainer {
  border-top:  1px solid var(--border) !important;
  padding:     1rem 3rem 1.25rem !important;
  max-width:   880px !important;
}

/* The visible input wrapper */
[data-testid="stChatInput"] {
  background:    var(--surface) !important;
  border:        1px solid var(--border) !important;
  border-radius: var(--r) !important;
  box-shadow:    0 2px 12px rgba(0,0,0,.25) !important;
  overflow:      hidden !important;
  transition:    border-color .15s, box-shadow .15s !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--accent) !important;
  box-shadow:   0 0 0 3px var(--accent-bg), 0 4px 16px rgba(0,0,0,.3) !important;
}

/* The textarea itself */
[data-testid="stChatInput"] textarea {
  background:     transparent !important;
  border:         none !important;
  outline:        none !important;
  box-shadow:     none !important;
  color:          var(--text) !important;
  font-family:    var(--sans) !important;
  font-size:      .9375rem !important;
  font-weight:    400 !important;
  line-height:    1.6 !important;
  caret-color:    var(--accent) !important;
  padding:        .85rem 1rem !important;
  resize:         none !important;
}
[data-testid="stChatInput"] textarea::placeholder {
  color:          var(--text3) !important;
  font-family:    var(--sans) !important;
  font-size:      .9375rem !important;
}

/* Send button */
[data-testid="stChatInput"] button {
  background:    var(--accent) !important;
  border:        none !important;
  border-radius: var(--r-sm) !important;
  margin:        .4rem .4rem .4rem 0 !important;
  padding:       .45rem .65rem !important;
  transition:    background .15s, transform .1s !important;
  cursor:        pointer !important;
}
[data-testid="stChatInput"] button:hover {
  background: var(--accent-dim) !important;
  transform:  scale(1.05) !important;
}
[data-testid="stChatInput"] button svg {
  fill: #fff !important;
}

/* ── Spinner ───────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--accent) !important; }
.stSpinner p {
  font-family:    var(--sans) !important;
  color:          var(--text2) !important;
  font-size:      .8125rem !important;
  letter-spacing: .02em !important;
}

/* ── Scrollbar ─────────────────────────────────────────── */
::-webkit-scrollbar       { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text3); }

/* ── Animations ────────────────────────────────────────── */
@keyframes msgIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
  0%,100% { opacity: 1; box-shadow: 0 0 0 0 var(--green); }
  50%     { opacity: .7; box-shadow: 0 0 0 3px transparent; }
}
@keyframes fadeIn {
  from { opacity: 0; } to { opacity: 1; }
}

/* ── Custom HTML component classes ─────────────────────── */

/* Header */
.header-wrap {
  padding: .25rem 0 1.5rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.75rem;
}
.header-top {
  display: flex;
  align-items: center;
  gap: .75rem;
  margin-bottom: .35rem;
}
.header-title {
  font-family:    var(--sans);
  font-size:      1.5rem;
  font-weight:    700;
  color:          var(--text);
  letter-spacing: -.025em;
}
.header-desc {
  font-family: var(--sans);
  font-size:   .875rem;
  color:       var(--text2);
  line-height: 1.6;
  max-width:   540px;
}
.badge {
  display:     inline-flex;
  align-items: center;
  gap:         .3rem;
  padding:     .2rem .65rem;
  border-radius: 20px;
  font-family:   var(--sans);
  font-size:     .72rem;
  font-weight:   600;
  letter-spacing:.02em;
  white-space:   nowrap;
}
.badge-green {
  background: var(--green-bg);
  color:      var(--green);
  border:     1px solid var(--green-bd);
}
.badge-blue {
  background: var(--accent-bg);
  color:      var(--accent);
  border:     1px solid var(--accent-bd);
}
.badge-orange {
  background: var(--orange-bg);
  color:      var(--orange);
  border:     1px solid rgba(251,146,60,.22);
}
.dot-live {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--green);
  animation:  pulse 2.5s ease infinite;
}

/* Suggested questions */
.suggest-wrap {
  display:   flex;
  flex-wrap: wrap;
  gap:       .5rem;
  margin:    1.5rem 0 .5rem;
  animation: fadeIn .4s ease;
}
.suggest-label {
  width:          100%;
  font-family:    var(--sans);
  font-size:      .72rem;
  font-weight:    700;
  text-transform: uppercase;
  letter-spacing: .08em;
  color:          var(--text3);
  margin-bottom:  .1rem;
}
.suggest-chip {
  display:       inline-flex;
  align-items:   center;
  gap:           .4rem;
  padding:       .45rem .85rem;
  background:    var(--surface2);
  border:        1px solid var(--border);
  border-radius: var(--r-sm);
  font-family:   var(--sans);
  font-size:     .8125rem;
  color:         var(--text2);
  cursor:        pointer;
  transition:    all .15s ease;
}
.suggest-chip:hover {
  background:   var(--surface3);
  border-color: var(--border2);
  color:        var(--text);
  transform:    translateY(-1px);
  box-shadow:   0 4px 12px rgba(0,0,0,.25);
}
.suggest-chip-icon {
  font-size: .75rem;
  opacity:   .6;
}

/* Sidebar brand */
.sb-brand {
  display:       flex;
  align-items:   center;
  gap:           .65rem;
  padding:       1.1rem 1rem 1rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1rem;
  background:    linear-gradient(145deg, rgba(59,130,246,.06) 0%, transparent 70%);
}
.sb-icon {
  width: 34px; height: 34px;
  background:    var(--accent-bg);
  border:        1px solid var(--accent-bd);
  border-radius: var(--r-sm);
  display:       flex;
  align-items:   center;
  justify-content: center;
  font-size:     1rem;
  flex-shrink:   0;
  box-shadow:    0 0 14px var(--accent-glow);
}
.sb-name {
  font-family:    var(--sans);
  font-size:      .9375rem;
  font-weight:    700;
  color:          var(--text);
  letter-spacing: -.015em;
  line-height:    1.2;
}
.sb-sub {
  font-family: var(--sans);
  font-size:   .7rem;
  color:       var(--text3);
  margin-top:  .05rem;
}

/* Sidebar sections */
.sb-section {
  padding: 0 .5rem;
}
.sb-label {
  font-family:    var(--sans);
  font-size:      .68rem;
  font-weight:    700;
  text-transform: uppercase;
  letter-spacing: .1em;
  color:          var(--text3);
  margin:         1.25rem 0 .5rem;
}
.kb-item {
  display:       flex;
  align-items:   center;
  justify-content: space-between;
  padding:       .32rem .5rem;
  border-radius: var(--r-sm);
  transition:    background .12s;
  cursor:        default;
}
.kb-item:hover { background: var(--surface2); }
.kb-left {
  display:     flex;
  align-items: center;
  gap:         .55rem;
}
.kb-icon {
  font-size:   .8rem;
  width:       18px;
  text-align:  center;
  flex-shrink: 0;
}
.kb-name {
  font-family: var(--sans);
  font-size:   .8rem;
  color:       var(--text2);
}
.kb-tag {
  font-family:    var(--sans);
  font-size:      .65rem;
  color:          var(--text3);
  background:     var(--surface3);
  border:         1px solid var(--border);
  border-radius:  4px;
  padding:        .05rem .35rem;
  letter-spacing: .02em;
}

/* Model chip in sidebar */
.model-chip {
  display:       flex;
  align-items:   center;
  gap:           .5rem;
  padding:       .5rem .75rem;
  background:    var(--surface2);
  border:        1px solid var(--border);
  border-radius: var(--r-sm);
  margin-top:    .35rem;
}
.model-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 6px var(--accent);
  flex-shrink: 0;
}
.model-name {
  font-family: var(--mono);
  font-size:   .8rem;
  color:       var(--text);
  font-weight: 500;
}
.model-tag {
  font-family:  var(--sans);
  font-size:    .65rem;
  color:        var(--green);
  background:   var(--green-bg);
  border:       1px solid var(--green-bd);
  border-radius:4px;
  padding:      .05rem .4rem;
  margin-left:  auto;
}

/* Sidebar footer */
.sb-footer {
  padding:    .75rem .5rem .5rem;
  border-top: 1px solid var(--border);
  margin-top: 1.25rem;
}
.sb-footer-row {
  display:         flex;
  justify-content: space-between;
  align-items:     center;
  padding:         .22rem 0;
}
.sb-footer-key {
  font-family:    var(--sans);
  font-size:      .72rem;
  color:          var(--text3);
  letter-spacing: .01em;
}
.sb-footer-val {
  font-family: var(--mono);
  font-size:   .7rem;
  color:       var(--text2);
}
</style>
"""

st.markdown(STYLES, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────── Sidebar ──
with st.sidebar:
    st.markdown("""
      <div class="sb-brand">
        <div class="sb-icon">🔐</div>
        <div>
          <div class="sb-name">CyberRAG</div>
          <div class="sb-sub">Threat Intelligence</div>
        </div>
      </div>
    """, unsafe_allow_html=True)

    # ── Provider ──
    st.markdown('<div class="sb-section"><div class="sb-label">Provider</div>', unsafe_allow_html=True)
    provider = st.selectbox("provider", ["Groq (Cloud)", "Ollama (Local)"], index=0, label_visibility="collapsed")
    is_groq = provider.startswith("Groq")

    # ── Groq API key ──
    if is_groq:
        env_key = os.environ.get("GROQ_API_KEY", "")
        st.markdown('<div class="sb-label">Groq API Key</div>', unsafe_allow_html=True)
        key_input = st.text_input(
            "groq_key",
            value=env_key,
            type="password",
            placeholder="gsk_...",
            label_visibility="collapsed",
        )
        groq_api_key = key_input or env_key or None
        if not groq_api_key:
            st.warning("Enter a Groq API key to use cloud models.", icon="⚠️")
    else:
        groq_api_key = None

    # ── Model ──
    model_list = GROQ_MODELS if is_groq else OLLAMA_MODELS
    st.markdown('<div class="sb-label">Model</div>', unsafe_allow_html=True)
    selected_model = st.selectbox("model", model_list, index=0, label_visibility="collapsed")
    st.markdown(f"""
      <div class="model-chip">
        <div class="model-dot"></div>
        <span class="model-name">{selected_model}</span>
        <span class="model-tag">{"Groq" if is_groq else "Local"}</span>
      </div>
    """, unsafe_allow_html=True)

    session_key = f"{provider}:{selected_model}"
    if st.session_state.get("current_model") != session_key:
        st.session_state["current_model"] = session_key
        st.session_state.messages = []

    kb_topics = [
        ("🎣", "Phishing",         "Social Eng."),
        ("💉", "SQL Injection",    "Web"),
        ("💰", "Ransomware",       "Malware"),
        ("🕳️", "Zero-day",         "Exploit"),
        ("🔀", "MITM Attacks",     "Network"),
        ("🌊", "DoS / DDoS",       "Availability"),
        ("🛡️", "Firewalls & IDS",  "Defense"),
        ("🔒", "Encryption",       "Crypto"),
        ("🔑", "Brute-force",      "Auth"),
        ("🦠", "Malware & Viruses","Malware"),
    ]
    st.markdown('<div class="sb-label">Knowledge Base</div>', unsafe_allow_html=True)
    for icon, name, tag in kb_topics:
        st.markdown(f"""
          <div class="kb-item">
            <div class="kb-left">
              <span class="kb-icon">{icon}</span>
              <span class="kb-name">{name}</span>
            </div>
            <span class="kb-tag">{tag}</span>
          </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown(f"""
      <div class="sb-footer">
        <div class="sb-footer-row">
          <span class="sb-footer-key">Embeddings</span>
          <span class="sb-footer-val">all-MiniLM-L6-v2</span>
        </div>
        <div class="sb-footer-row">
          <span class="sb-footer-key">Vector DB</span>
          <span class="sb-footer-val">ChromaDB</span>
        </div>
        <div class="sb-footer-row">
          <span class="sb-footer-key">Provider</span>
          <span class="sb-footer-val">{"Groq" if is_groq else "Ollama"}</span>
        </div>
        <div class="sb-footer-row">
          <span class="sb-footer-key">Framework</span>
          <span class="sb-footer-val">LangChain 1.x</span>
        </div>
        <div class="sb-footer-row">
          <span class="sb-footer-key">Articles</span>
          <span class="sb-footer-val">15 indexed</span>
        </div>
      </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────── Agent ──
@st.cache_resource(show_spinner="Loading model and vector store...")
def get_agent(model: str, provider: str, groq_api_key: str | None):
    return build_agent(model=model, provider=provider, groq_api_key=groq_api_key)

_provider_id = "groq" if is_groq else "ollama"
agent = get_agent(selected_model, _provider_id, groq_api_key)


# ─────────────────────────────────────────────────── Header ──
st.markdown(f"""
  <div class="header-wrap">
    <div class="header-top">
      <span class="header-title">Cybersecurity Assistant</span>
      <span class="badge badge-green"><div class="dot-live"></div>Online</span>
      <span class="badge badge-blue">{selected_model}</span>
    </div>
    <p class="header-desc">
      Ask about threats, attack vectors, defense strategies, or encryption.
      The agent searches a curated knowledge base and cites sources.
    </p>
  </div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────── Chat history ──
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "Hello! I'm your cybersecurity assistant. I can answer questions about "
            "threats, attack vectors, defense strategies, encryption, malware, and more.\n\n"
            "What would you like to know?"
        ),
    }]

# Suggested questions — only shown before any user message
has_user_msg = any(m["role"] == "user" for m in st.session_state.messages)
if not has_user_msg:
    chips = "".join(
        f'<div class="suggest-chip"><span class="suggest-chip-icon">↗</span>{q}</div>'
        for q in SUGGESTED
    )
    st.markdown(f"""
      <div class="suggest-wrap">
        <div class="suggest-label">Suggested questions</div>
        {chips}
      </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    avatar = "🔐" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])


# ──────────────────────────────────────────── Chat input ──
if prompt := st.chat_input("Ask a cybersecurity question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🔐"):
        with st.spinner("Searching knowledge base..."):
            try:
                response = run_agent(agent, prompt)
            except Exception as e:
                response = f"An error occurred: {str(e)}"
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
