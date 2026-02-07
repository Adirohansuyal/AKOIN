import os
from groq import Groq
from dotenv import load_dotenv

# -----------------------------------
# Load environment variables
# -----------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables.")

# -----------------------------------
# Initialize Groq Client
# -----------------------------------

client = Groq(api_key=GROQ_API_KEY)

# -----------------------------------
# System Prompt
# -----------------------------------

SYSTEM_PROMPT = """
You are a regulatory reporting assistant.

Return ONLY valid JSON.

Do NOT include:
- Explanations
- Markdown
- Text before JSON
- Text after JSON

Schema:

{
  "template": "C01.00",
  "fields": [
    {
      "code": "string",
      "label": "string",
      "value": number,
      "source_rule": "string"
    }
  ],
  "missing_data": [],
  "validation_flags": []
}
"""

# -----------------------------------
# LLM Function
# -----------------------------------

def generate_structured_output(query, context):

    prompt = f"""
Context:
{context}

User Scenario:
{query}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content
