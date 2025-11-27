import streamlit as st
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv
from repo_fetcher import fetch_repository_docs
from ai_summarizer import summarize_markdown_files
from html_builder import generate_onboarding_html, save_html_file

# Load environment variables from .env file
load_dotenv()

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

if "html_content" not in st.session_state:
    st.session_state["html_content"] = None

if "html_error" not in st.session_state:
    st.session_state["html_error"] = None



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


def do_generate_html():
    if not st.session_state["summaries"]:
        st.session_state["html_error"] = "No summaries to generate HTML from."
        return
    
    try:
        # Get additional metadata
        author = st.session_state.get("author_input", "AI Assistant")
        company = st.session_state.get("company_input", "Your Company")
        
        html_content = generate_onboarding_html(
            summaries=st.session_state["summaries"],
            repo_meta=st.session_state["repo_meta"],
            author=author,
            company=company
        )
        
        st.session_state["html_content"] = html_content
        st.session_state["html_error"] = None
    
    except Exception as e:
        st.session_state["html_error"] = str(e)

# ---------------- INPUT ----------------

repo_url = st.text_input(
    "GitHub Repository URL",
    key="repo_input",
    placeholder="https://github.com/user/repo"
)

# Additional inputs for HTML generation
col1, col2 = st.columns(2)
with col1:
    author = st.text_input(
        "Author Name",
        key="author_input", 
        value="AI Assistant",
        placeholder="Your name"
    )

with col2:
    company = st.text_input(
        "Company Name", 
        key="company_input",
        value="Your Company",
        placeholder="Company or organization"
    )

# Check if API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ OpenAI API key not found. Please add OPENAI_API_KEY to your .env file")
else:
    st.success("✅ OpenAI API key loaded successfully")

# ---------------- BUTTONS ----------------

st.button("Fetch Documentation", on_click=do_fetch)

st.button(
    "Summarize with AI",
    on_click=do_summarize,
    disabled=st.session_state["markdown_files"] is None
)

st.button(
    "Generate HTML Document",
    on_click=do_generate_html,
    disabled=st.session_state["summaries"] is None
)

# Download button for HTML
if st.session_state["html_content"]:
    st.download_button(
        label="📄 Download HTML Document",
        data=st.session_state["html_content"],
        file_name=f"{st.session_state['repo_meta']['repo']}_onboarding.html",
        mime="text/html"
    )

# ---------------- COLLAPSIBLE OUTPUT ----------------

with st.expander("📄 Fetched Documentation", expanded=False):
    if st.session_state["fetch_error"]:
        st.error(st.session_state["fetch_error"])
    elif st.session_state["markdown_files"]:
        # Show summary stats
        num_files = len(st.session_state["markdown_files"])
        num_images = len(st.session_state.get("repo_meta", {}).get("image_files", []))
        
        st.info(f"📊 Found {num_files} markdown files and {num_images} images")
        
        # Show images if any
        if num_images > 0:
            with st.expander("🖼️ Images Found", expanded=False):
                for img_path in st.session_state["repo_meta"]["image_files"]:
                    st.code(img_path, language="text")
        
        # Show markdown content
        for path, content in st.session_state["markdown_files"].items():
            with st.expander(f"📝 {path}", expanded=False):
                st.code(content, language="markdown")

with st.expander("🤖 AI Summary Preview", expanded=False):
    if st.session_state["summary_error"]:
        st.error(st.session_state["summary_error"])
    elif st.session_state["summaries"]:
        for path, summary in st.session_state["summaries"].items():
            with st.expander(f"📋 {path}", expanded=False):
                st.markdown(summary)

with st.expander("📄 HTML Document Preview", expanded=False):
    if st.session_state["html_error"]:
        st.error(st.session_state["html_error"])
    elif st.session_state["html_content"]:
        st.success("✅ HTML document generated successfully!")
        
        # Show HTML preview in an iframe
        components.html(
            st.session_state["html_content"],
            height=600,
            scrolling=True
        )

