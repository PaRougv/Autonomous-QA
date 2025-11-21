import os
import json
import requests
import streamlit as st

from typing import List
from backend.server import start_backend_server

start_backend_server()
# -------------------------- CONFIG & STYLES -------------------------- #

DEFAULT_BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Autonomous QA Agent",
    page_icon="🧪",
    layout="wide",
)

# ---- Custom CSS to make things not look like default Streamlit ---- #
st.markdown(
    """
    <style>
    /* Global */
    body {
        background: radial-gradient(circle at top left, #111827, #020617);
    }
    .main {
        background: linear-gradient(135deg, #020617 0%, #020617 50%, #020617 100%);
        color: #e5e7eb;
    }

    /* Hero section */
    .hero {
        padding: 1.5rem 1.75rem;
        border-radius: 1.5rem;
        background: radial-gradient(circle at top left, #1f2937, #020617);
        border: 1px solid rgba(148, 163, 184, 0.25);
        box-shadow:
            0 18px 40px rgba(15, 23, 42, 0.9),
            0 0 0 1px rgba(15, 23, 42, 0.9);
    }
    .hero-title {
        font-size: 1.9rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        margin-bottom: 0.3rem;
        color: #e5e7eb;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #9ca3af;
        margin-bottom: 0.6rem;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        background: rgba(55, 65, 81, 0.85);
        color: #d1d5db;
        font-size: 0.75rem;
        border: 1px solid rgba(75, 85, 99, 0.9);
    }
    .hero-badge-dot {
        width: 7px;
        height: 7px;
        border-radius: 999px;
        background: #22c55e;
        box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.28);
    }

    /* Step header */
    .step-header {
        font-weight: 600;
        font-size: 1.05rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin-bottom: 0.3rem;
    }
    .step-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 1.3rem;
        height: 1.3rem;
        border-radius: 999px;
        background: rgba(59, 130, 246, 0.15);
        color: #bfdbfe;
        font-size: 0.72rem;
        border: 1px solid rgba(59, 130, 246, 0.6);
    }
    .step-caption {
        font-size: 0.8rem;
        color: #9ca3af;
        margin-bottom: 0.4rem;
    }

    /* Card */
    .card {
        border-radius: 1rem;
        padding: 0.9rem 1rem;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(75, 85, 99, 0.65);
        box-shadow: 0 12px 25px rgba(15, 23, 42, 0.9);
    }

    /* Status chips */
    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        font-size: 0.7rem;
        border: 1px solid rgba(55, 65, 81, 0.9);
        background: rgba(17, 24, 39, 0.8);
        color: #9ca3af;
    }
    .status-dot-green {
        width: 6px;
        height: 6px;
        border-radius: 999px;
        background: #22c55e;
    }
    .status-dot-amber {
        width: 6px;
        height: 6px;
        border-radius: 999px;
        background: #f97316;
    }

    /* Code / JSON blocks tweaks */
    .stCode, pre {
        border-radius: 0.75rem !important;
        border: 1px solid rgba(55, 65, 81, 0.8) !important;
        background: #020617 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------- SIDEBAR -------------------------- #

st.sidebar.title("⚙️ Settings")

backend_url = st.sidebar.text_input(
    "Backend URL",
    value=DEFAULT_BACKEND_URL,
    help="FastAPI backend base URL.",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
**Workflow**

1. 📚 Build Knowledge Base  
2. 🧪 Generate Test Cases  
3. 🤖 Generate Selenium Scripts  
    """
)

st.sidebar.markdown("---")
st.sidebar.caption("Tip: keep this page + your backend terminal visible while recording your demo.")

# -------------------------- HERO SECTION -------------------------- #

st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">
            <div class="hero-badge-dot"></div>
            Autonomous QA · RAG + LLM + Selenium
        </div>
        <div style="margin-top: 0.6rem;">
            <div class="hero-title">
                Autonomous QA Agent for Web Checkout Testing
            </div>
            <div class="hero-subtitle">
                Upload your project docs & checkout page. The agent builds a testing brain, generates grounded test cases,
                and then turns them into runnable Selenium scripts.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("")

# -------------------------- SESSION STATE -------------------------- #

if "test_cases" not in st.session_state:
    st.session_state.test_cases: List[dict] = []

if "raw_test_case_output" not in st.session_state:
    st.session_state.raw_test_case_output = ""

if "kb_status" not in st.session_state:
    st.session_state.kb_status = "idle"  # idle | built | error

# -------------------------- LAYOUT: TABS -------------------------- #

tab1, tab2, tab3 = st.tabs(
    ["1. Build Knowledge Base", "2. Generate Test Cases", "3. Generate Selenium Scripts"]
)

# -------------------------- TAB 1: BUILD KB -------------------------- #

with tab1:
    st.markdown(
        """
        <div class="step-header">
            <div class="step-pill">1</div>
            <span>Build Knowledge Base from Documentation + HTML</span>
        </div>
        <div class="step-caption">
            Ingest support documents (business rules, APIs, UX guidelines) and the checkout HTML into a searchable vector store.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_uploads, col_info = st.columns([1.35, 1])

    with col_uploads:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        support_files = st.file_uploader(
            "📁 Support Documents (MD, TXT, JSON)",
            type=["md", "txt", "json"],
            accept_multiple_files=True,
            help="Upload requirement docs, rules, API specs, UX notes, etc.",
        )

        checkout_file = st.file_uploader(
            "🧾 checkout.html",
            type=["html"],
            accept_multiple_files=False,
            help="Upload the actual checkout page HTML to ground selectors.",
        )

        build_clicked = st.button("📚 Build Knowledge Base", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_info:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**What happens in this step?**")
        st.markdown(
            """
            - 🔍 Text is chunked and embedded using a SentenceTransformer  
            - 🧠 Chunks are stored in a simple vector store (`kb_store.pkl`)  
            - 🧾 Full `checkout.html` is stored for Selenium selector generation  

            **Recommended uploads:**
            - `product_specs.md`  
            - `ui_ux_guide.txt`  
            - `api_endpoints.json`  
            - `checkout.html`
            """
        )

        if st.session_state.kb_status == "built":
            st.markdown(
                """
                <div class="status-chip">
                    <div class="status-dot-green"></div>
                    Knowledge base is ready. You can move to step 2.
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif st.session_state.kb_status == "error":
            st.markdown(
                """
                <div class="status-chip">
                    <div class="status-dot-amber"></div>
                    Last build attempt failed. Check the error message below.
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    if build_clicked:
        docs_payload = []

        # Support docs
        if support_files:
            for f in support_files:
                content = f.read().decode("utf-8", errors="ignore")
                docs_payload.append(
                    {
                        "filename": f.name,
                        "content": content,
                        "doc_type": "support",
                    }
                )

        # checkout.html
        if checkout_file is not None:
            html_content = checkout_file.read().decode("utf-8", errors="ignore")
            docs_payload.append(
                {
                    "filename": checkout_file.name,
                    "content": html_content,
                    "doc_type": "html",
                }
            )

        if not docs_payload:
            st.error("Please upload at least one support document and/or `checkout.html` before building the KB.")
            st.session_state.kb_status = "error"
        else:
            with st.spinner("Indexing documents and building embeddings…"):
                try:
                    resp = requests.post(
                        f"{backend_url}/build_kb",
                        json={"documents": docs_payload},
                        timeout=600,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(
                            f"✅ Knowledge Base Built — **{data['num_chunks']}** text chunks indexed."
                        )
                        st.session_state.kb_status = "built"
                    else:
                        st.error(f"Backend error: {resp.status_code} - {resp.text}")
                        st.session_state.kb_status = "error"
                except Exception as e:
                    st.error(f"Error calling backend: {e}")
                    st.session_state.kb_status = "error"


# -------------------------- TAB 2: GENERATE TEST CASES -------------------------- #

with tab2:
    st.markdown(
        """
        <div class="step-header">
            <div class="step-pill">2</div>
            <span>Generate Grounded Test Cases</span>
        </div>
        <div class="step-caption">
            Ask the agent what you want to test. It will use RAG over your docs + HTML to propose structured test cases
            (ID, feature, scenario, steps, expected result).
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_query, col_status = st.columns([1.4, 1])

    with col_query:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        query = st.text_area(
            "🧪 What should the agent test?",
            placeholder="Examples:\n- Generate positive and negative test cases for discount code and shipping.\n- Create edge case tests for form validation and email field.\n- Generate test cases for empty cart, invalid coupon, and payment flow.",
            height=120,
        )

        gen_clicked = st.button("🧪 Generate Test Cases", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_status:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Tips for good prompts**")
        st.markdown(
            """
            - Mention **features**: discount code, shipping, cart, form.  
            - Ask for **positive + negative** cases.  
            - Scope it: “for discount only”, or “for complete checkout”.  

            Example prompt:
            > Generate positive and negative test cases for discount code SAVE15, express shipping, and form validation.
            """
        )
        if st.session_state.test_cases:
            st.markdown(
                f"Parsed **{len(st.session_state.test_cases)}** test cases from the last run."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    if gen_clicked:
        if not query.strip():
            st.error("Please describe what you want to test.")
        else:
            with st.spinner("Asking the Test Case Agent to propose scenarios…"):
                try:
                    resp = requests.post(
                        f"{backend_url}/generate_test_cases",
                        json={"query": query},
                        timeout=600,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.raw_test_case_output = data.get("raw_output", "")
                        st.session_state.test_cases = data.get("test_cases", [])

                        if not st.session_state.test_cases:
                            st.warning(
                                "The LLM responded, but I couldn't parse structured test cases. "
                                "Check the raw output below."
                            )
                        else:
                            st.success(
                                f"Generated and parsed **{len(st.session_state.test_cases)}** structured test cases."
                            )
                    else:
                        st.error(f"Backend error: {resp.status_code} - {resp.text}")
                except Exception as e:
                    st.error(f"Error calling backend: {e}")

    st.markdown("### Raw LLM Output (for debugging or manual inspection)")
    st.code(
        st.session_state.raw_test_case_output or "No test cases generated yet.",
        language="json",
    )

    if st.session_state.test_cases:
        st.markdown("### Parsed Test Cases")
        cases = st.session_state.test_cases
        options = [f"{c['id']} | {c['feature']} | {c['scenario']}" for c in cases]
        selected = st.selectbox(
            "Select a test case for Selenium script generation:",
            options,
        )

        selected_index = options.index(selected)
        selected_case = cases[selected_index]

        st.markdown("#### Selected Test Case (Structured)")
        st.json(selected_case)
        st.info(
            "You can now switch to **Step 3** tab to generate an automation script from this test case.",
            icon="➡️",
        )
        # Keep the selected case in state for tab 3
        st.session_state.selected_case = selected_case
    else:
        st.info("Once structured test cases are generated, they will appear here for selection.")


# -------------------------- TAB 3: GENERATE SELENIUM SCRIPTS -------------------------- #

with tab3:
    st.markdown(
        """
        <div class="step-header">
            <div class="step-pill">3</div>
            <span>Generate Selenium Automation Script</span>
        </div>
        <div class="step-caption">
            Turn a selected test case into a runnable Selenium Python script, grounded in the real checkout HTML.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)

    if "selected_case" not in st.session_state:
        st.warning("First generate test cases in **Step 2** and select one there.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        selected_case = st.session_state.selected_case

        st.markdown("#### Test Case Input")
        st.json(selected_case)

        if st.button("🤖 Generate Selenium Script for This Test Case", use_container_width=True):
            with st.spinner("Asking the Script Generation Agent to produce a runnable Selenium test…"):
                try:
                    resp = requests.post(
                        f"{backend_url}/generate_selenium_script",
                        json={"test_case": selected_case},
                        timeout=600,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        script_text = data.get("script", "")
                        if not script_text.strip():
                            st.error("The agent did not return any script.")
                        else:
                            st.success("Selenium script generated. You can copy it into a test file and run it.")
                            st.markdown("#### Generated Selenium Python Script")
                            st.code(script_text, language="python")
                            st.caption(
                                "Tip: save this as `tests/test_something.py` and run it with "
                                "`python tests/test_something.py` in your virtualenv."
                            )
                    else:
                        st.error(f"Backend error: {resp.status_code} - {resp.text}")
                except Exception as e:
                    st.error(f"Error calling backend: {e}")

        st.markdown("</div>", unsafe_allow_html=True)
