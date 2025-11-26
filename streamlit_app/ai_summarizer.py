import os
import time
from openai import OpenAI
from openai import RateLimitError

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_markdown_files(markdown_files, image_files):
    summaries = {}

    for path, content in markdown_files.items():

        # Detect images in same directory
        folder = os.path.dirname(path)
        has_images = any(img.startswith(folder) for img in image_files)

        prompt = f"""
Summarize the following markdown file in 3–5 concise sentences.
If the document contains diagrams or images, mention that.
Always end with:
"For full details, refer to: {path}"

CONTENT:
{content}
"""

        # Rate-limit-safe call with retry
        while True:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",     # <-- CHEAPER + HIGHER LIMITS
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
                break

            except RateLimitError:
                print("Rate limit hit, waiting 2 seconds...")
                time.sleep(2)

        # Sleep between calls to avoid TPM limit
        time.sleep(0.3)

    return summaries
