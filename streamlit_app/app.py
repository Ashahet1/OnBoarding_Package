import streamlit as st
from repo_fetcher import fetch_repository_docs
from ai_summarizer import summarize_markdown_files

st.set_page_config(page_title="Onboarding PDF Generator", layout="wide")

st.title("Onboarding Knowledge Pack Generator")

# ---------------- STATE INIT ----------------
if "markdown_files" not in st.session_state:
    st.session_state["markdown_files"] = None

if "repo_meta" not in st.session_state:
    st.session_state["repo_meta"] = None

if "summaries" not in st.session_state:
    st.session_state["summaries"] = None

if "fetch_error" not in st.session_state:
    st.session_state["fetch_error"] = None

if "summary_error" not in st.session_state:
    st.session_state["summary_error"] = None

if "trigger_fetch" not in st.session_state:
    st.session_state["trigger_fetch"] = False

if "trigger_summarize" not in st.session_state:
    st.session_state["trigger_summarize"] = False



# ---------------- CALLBACKS ----------------

def do_fetch():
    url = st.session_state["repo_input"]
    if not url.strip():
        st.session_state["fetch_error"] = "Please enter a GitHub URL."
        return
    
    try:
        data = fetch_repository_docs(url)
        markdown = data.get("markdown_files", {})

        if not markdown:
            st.session_state["fetch_error"] = "No markdown files found."
            return
        
        st.session_state["markdown_files"] = markdown
        st.session_state["repo_meta"] = data
        st.session_state["fetch_error"] = None

    except Exception as e:
        st.session_state["fetch_error"] = str(e)


def do_summarize():
    if not st.session_state["markdown_files"]:
        st.session_state["summary_error"] = "No docs to summarize."
        return
    
    try:
        summaries = summarize_markdown_files(
            st.session_state["markdown_files"],
            st.session_state["repo_meta"]["image_files"]
        )
        st.session_state["summaries"] = summaries
        st.session_state["summary_error"] = None
    
    except Exception as e:
        st.session_state["summary_error"] = str(e)

# ---------------- INPUT ----------------

repo_url = st.text_input(
    "GitHub Repository URL",
    key="repo_input",
    placeholder="https://github.com/user/repo"
)

# ---------------- BUTTONS ----------------

st.button("Fetch Documentation", on_click=do_fetch)

st.button(
    "Summarize with AI",
    on_click=do_summarize,
    disabled=st.session_state["markdown_files"] is None
)

st.button(
    "Generate PDF",
    disabled=st.session_state["summaries"] is None
)

# ---------------- COLLAPSIBLE OUTPUT ----------------

with st.expander("📄 Fetched Documentation", expanded=False):
    if st.session_state["fetch_error"]:
        st.error(st.session_state["fetch_error"])
    elif st.session_state["markdown_files"]:
        text = ""
        for path, content in st.session_state["markdown_files"].items():
            text += f"### {path}\n```\n{content}\n```\n\n"
        st.markdown(text)

with st.expander("🤖 AI Summary Preview", expanded=False):
    if st.session_state["summary_error"]:
        st.error(st.session_state["summary_error"])
    elif st.session_state["summaries"]:
        text = ""
        for path, summary in st.session_state["summaries"].items():
            text += f"### {path}\n{summary}\n\n"
        st.markdown(text)

