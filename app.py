import time
import streamlit as st
from agents import build_reader_agent, build_search_agent, critic_chain, writer_chain

# Page Config
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom Styling
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;700&display=swap');

/* Main Background & Fonts */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}

.stApp {
    background: #0b0b0e;
    background-image: 
        radial-gradient(ellipse 70% 40% at 50% -10%, rgba(255, 123, 0, 0.15) 0%, transparent 70%);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 3rem 4rem 4rem; max-width: 1200px; }

/* Hero Section Header */
.hero { text-align: center; margin-bottom: 2.5rem; }
.hero-eyebrow {
    font-family: 'DM Mono', monospace; font-size: 0.75rem; font-weight: 500;
    letter-spacing: 0.25em; text-transform: uppercase; color: #ff7b00; margin-bottom: 1rem;
}

/* Exact Headline Colors: "Research" in Light Cream/White, "Mind" in Neon Orange */
.hero h1 {
    font-family: 'Syne', sans-serif; font-size: clamp(3rem, 6vw, 4.5rem);
    font-weight: 800; line-height: 1.0; color: #e8e4dc !important; margin: 0 0 1rem;
    letter-spacing: -0.02em;
}
.hero h1 span { color: #ff7b00 !important; }

.hero-sub { font-size: 0.95rem; color: #8e8a85; max-width: 580px; margin: 0 auto; line-height: 1.6; }

/* Input Card */
.stTextInput > div > div > input {
    background-color: #141419 !important;
    color: #ffffff !important;
    border: 1px solid #22222a !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
}

/* Custom Orange Button */
.stButton > button {
    background: linear-gradient(135deg, #ff7b00 0%, #e65c00 100%) !important;
    color: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.5rem !important;
    box-shadow: 0 4px 20px rgba(255, 123, 0, 0.3) !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    box-shadow: 0 6px 25px rgba(255, 123, 0, 0.5) !important;
    transform: translateY(-1px);
}

/* Step Card Design */
.step-card {
    background: #121217;
    border: 1px solid #1c1c24;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
    transition: all 0.2s ease;
}
.step-card.active { border-color: rgba(255,123,0,0.6); background: rgba(255,123,0,0.03); }
.step-card.done { border-color: rgba(80,200,120,0.4); background: rgba(80,200,120,0.02); }

.step-header { display: flex; align-items: center; justify-content: space-between; }
.step-num { font-family: 'DM Mono', monospace; font-size: 0.75rem; color: #ff7b00; margin-right: 0.6rem; }
.step-title { font-family: 'Syne', sans-serif; font-size: 0.95rem; font-weight: 700; color: #ffffff; }
.step-status { font-family: 'DM Mono', monospace; font-size: 0.68rem; letter-spacing: 0.1em; }
.status-waiting { color: #4a4a52; }
.status-running { color: #ff7b00; }
.status-done { color: #50c878; }
.step-desc { font-size: 0.8rem; color: #63636e; margin-top: 0.3rem; }

/* Panels for Report and Critic */
.report-panel {
    background: #111116; border: 1px solid #22222e;
    border-radius: 14px; padding: 2rem; margin-top: 2rem;
}
.panel-label {
    font-family: 'DM Mono', monospace; font-size: 0.75rem; letter-spacing: 0.15em;
    text-transform: uppercase; margin-bottom: 1.2rem; padding-bottom: 0.6rem;
}
.panel-label.orange { color: #ff7b00; border-bottom: 1px solid rgba(255,123,0,0.2); }
.panel-label.green { color: #50c878; border-bottom: 1px solid rgba(80,200,120,0.2); }
</style>
""",
    unsafe_allow_html=True,
)


def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done": ("✓ DONE", "status-done"),
    }
    label, cls = status_map.get(state, ("WAITING", "status-waiting"))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(
        f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <div>
                <span class="step-num">{num}</span>
                <span class="step-title">{title}</span>
            </div>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div class='step-desc'>" + desc + "</div>" if desc else ""}
    </div>
    """,
        unsafe_allow_html=True,
    )


# Session State Initialization
if "results" not in st.session_state:
    st.session_state.results = {}
if "current_step" not in st.session_state:
    st.session_state.current_step = None

# Hero Header: "Research" in Off-White, "Mind" in Neon Orange
st.markdown(
    """
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

col_input, col_spacer, col_pipeline = st.columns([5, 0.4, 4.6])

with col_input:
    st.markdown(
        "<div style='font-family:\"DM Mono\", monospace; font-size:0.75rem; letter-spacing:0.1em; color:#ff7b00; margin-bottom:0.5rem;'>RESEARCH TOPIC</div>",
        unsafe_allow_html=True,
    )

    topic_val = st.text_input(
        "Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2026",
        label_visibility="collapsed",
    )

    run_btn = st.button("⚡ Run Research Pipeline", use_container_width=True)

    st.markdown(
        """
    <div style="margin-top: 1.5rem;">
        <div style="font-size: 0.75rem; color: #555560; font-family: 'DM Mono', monospace; margin-bottom: 0.6rem;">TRY →</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Suggestion Chips
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("LLM agents 2026", key="chip1"):
            topic_val = "LLM agents 2026"
    with c2:
        if st.button("CRISPR gene editing", key="chip2"):
            topic_val = "CRISPR gene editing"
    with c3:
        if st.button("Fusion energy progress", key="chip3"):
            topic_val = "Fusion energy progress"

with col_pipeline:
    st.markdown(
        "<div style='font-family:\"Syne\", sans-serif; font-size:1.3rem; font-weight:800; color:#ffffff; margin-bottom:1.2rem;'>Pipeline</div>",
        unsafe_allow_html=True,
    )

    r = st.session_state.results

    def get_status(step_name):
        if step_name in r:
            return "done"
        if st.session_state.current_step == step_name:
            return "running"
        return "waiting"

    step_card(
        "01",
        "Search Agent",
        get_status("search"),
        "Gathers recent web information",
    )
    step_card(
        "02",
        "Reader Agent",
        get_status("reader"),
        "Scrapes & extracts deep content",
    )
    step_card(
        "03", "Writer Chain", get_status("writer"), "Drafts the full report"
    )
    step_card(
        "04", "Critic Chain", get_status("critic"), "Reviews & scores report"
    )

if run_btn:
    if not topic_val or not topic_val.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.current_step = "search"
        st.rerun()

# Run agent executions sequentially across reruns
if st.session_state.current_step == "search":
    with st.spinner("🔍 Gathering web sources..."):
        search_agent = build_search_agent()
        sr = search_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Find recent information about: {topic_val}",
                    )
                ]
            }
        )
        st.session_state.results["search"] = sr["output"]
        st.session_state.current_step = "reader"
        st.rerun()

elif st.session_state.current_step == "reader":
    with st.spinner("📄 Reader Agent scraping content..."):
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Scrape the best URL from these search results:\n{st.session_state.results['search'][:1000]}",
                    )
                ]
            }
        )
        st.session_state.results["reader"] = rr["output"]
        st.session_state.current_step = "writer"
        st.rerun()

elif st.session_state.current_step == "writer":
    with st.spinner("✍️ Writing research report..."):
        combined = f"SEARCH:\n{st.session_state.results['search']}\n\nSCRAPED:\n{st.session_state.results['reader']}"
        st.session_state.results["writer"] = writer_chain.invoke(
            {"topic": topic_val, "research": combined}
        )
        st.session_state.current_step = "critic"
        st.rerun()

elif st.session_state.current_step == "critic":
    with st.spinner("🧐 Critic reviewing report..."):
        st.session_state.results["critic"] = critic_chain.invoke(
            {"report": st.session_state.results["writer"]}
        )
        st.session_state.current_step = None
        st.rerun()

# Display Results Below
r = st.session_state.results
if "writer" in r:
    st.markdown(
        '<div class="report-panel"><div class="panel-label orange">📝 Final Research Report</div>',
        unsafe_allow_html=True,
    )
    st.markdown(r["writer"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.download_button(
        label="⬇ Download Report (.md)",
        data=r["writer"],
        file_name=f"research_report_{int(time.time())}.md",
        mime="text/markdown",
    )

    if "critic" in r:
        st.markdown(
            '<div class="report-panel"><div class="panel-label green">🧐 Critic Evaluation</div>',
            unsafe_allow_html=True,
        )
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)