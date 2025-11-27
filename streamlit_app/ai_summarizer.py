import os
import time
import ssl
import urllib3
from openai import OpenAI
from openai import RateLimitError, OpenAIError

# Disable SSL warnings for debugging (not recommended for production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_openai_client():
    """Get OpenAI client with API key from environment"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    # Try with default settings first
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        print(f"Standard client failed: {e}")
        # Try with custom HTTP client for SSL issues
        import httpx
        custom_client = httpx.Client(
            verify=False,  # Disable SSL verification as workaround
            timeout=30.0
        )
        return OpenAI(api_key=api_key, http_client=custom_client)

def summarize_markdown_files(markdown_files, image_files):
    summaries = {}
    
    try:
        # Initialize client here, after environment variables are loaded
        client = get_openai_client()
        print("✅ OpenAI client initialized successfully")
    except Exception as e:
        error_msg = f"Failed to initialize OpenAI client: {str(e)}"
        print(error_msg)
        # Return error summaries for all files
        for path in markdown_files.keys():
            summaries[path] = f"❌ {error_msg}"
        return summaries

    for path, content in markdown_files.items():
        try:
            print(f"Processing {path}...")
            
            # Detect images in same directory
            folder = os.path.dirname(path)
            has_images = any(img.startswith(folder) for img in image_files)

            prompt = f"""
Summarize the following markdown file in 3–5 concise sentences.
If the document contains diagrams or images, mention that.
Always end with:
"For full details, refer to: {path}"

CONTENT:
{content[:2000]}...
"""  # Truncate content to avoid token limits

            # Rate-limit-safe call with retry
            max_retries = 2  # Reduced retries for faster feedback
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",     # <-- CHEAPER + HIGHER LIMITS
                        messages=[
                            {"role": "system", "content": "You are an expert technical writer."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=200,
                        temperature=0.2
                    )

                    summary_text = response.choices[0].message.content.strip()

                    if has_images:
                        summary_text += "\n\nNote: This section includes images or diagrams."

                    summaries[path] = summary_text
                    print(f"✅ {path} processed successfully")
                    break

                except RateLimitError:
                    print(f"Rate limit hit, waiting 2 seconds... (retry {retry_count + 1}/{max_retries})")
                    time.sleep(2)
                    retry_count += 1
                    
                except OpenAIError as e:
                    print(f"OpenAI API error for {path}: {str(e)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(1)
                    else:
                        summaries[path] = f"❌ API Error: Connection issues. Please check your internet connection and firewall settings."
                        break
                        
                except Exception as e:
                    print(f"Unexpected error for {path}: {str(e)}")
                    summaries[path] = f"❌ Error: {str(e)}"
                    break

            # Sleep between calls to avoid TPM limit
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error processing {path}: {str(e)}")
            summaries[path] = f"❌ Processing error: {str(e)}"

    return summaries
