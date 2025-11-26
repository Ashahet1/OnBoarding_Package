import requests
from urllib.parse import urlparse

GITHUB_API_BASE = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"

SUPPORTED_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".svg")


def parse_repo_url(repo_url: str):
    """Extract owner and repo from a GitHub URL."""
    parsed = urlparse(repo_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL. Expected format: https://github.com/owner/repo")
    return parts[0], parts[1]


def get_repo_default_branch(owner: str, repo: str):
    """Fetch default branch for the repo (main/master)."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json().get("default_branch", "main")


def get_repo_tree(owner: str, repo: str, branch: str):
    """Fetch full recursive file tree for the repo."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json().get("tree", [])


def download_raw_file(owner: str, repo: str, branch: str, path: str):
    """Download raw file content from GitHub."""
    raw_url = f"{RAW_BASE}/{owner}/{repo}/{branch}/{path}"
    resp = requests.get(raw_url)
    if resp.status_code == 200:
        return resp.text
    return None


def fetch_repository_docs(repo_url: str):
    """Main function to fetch ALL markdown files and ALL images."""
    owner, repo = parse_repo_url(repo_url)
    branch = get_repo_default_branch(owner, repo)

    tree = get_repo_tree(owner, repo, branch)

    markdown_files = {}
    image_files = []

    for item in tree:
        if item["type"] != "blob":
            continue

        path = item["path"].lower()

        # Collect markdown files
        if path.endswith(".md"):
            content = download_raw_file(owner, repo, branch, item["path"])
            if content:
                markdown_files[item["path"]] = content

        # Collect images (full paths only)
        if path.endswith(SUPPORTED_IMAGE_EXTENSIONS):
            image_files.append(item["path"])

    return {
        "markdown_files": markdown_files,   # dict: path → content
        "image_files": image_files,         # list of relative paths
        "branch": branch,
        "repo": repo,
        "owner": owner
    }
