from fastapi import FastAPI, Query
import json
import os
from groq import Groq

# ==============================
# GROQ CLIENT
# ==============================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ==============================
# FASTAPI INIT
# ==============================

app = FastAPI(
    title="COREP Reporting Assistant",
    version="1.0"
)

# ==============================
# REGULATORY CORPUS
# ==============================

REGULATORY_RULES = [
    {
        "id": "Article 26",
        "text": """
Article 26 – Common Equity Tier 1 Capital (CET1)

Includes:
• Ordinary share capital
• Retained earnings
• Accumulated OCI

Reported in COREP Template C01.00 – Field 010.
"""
    },
    {
        "id": "Article 51",
        "text": """
Article 51 – Additional Tier 1 Capital (AT1)

Includes:
• Perpetual subordinated instruments
• Hybrid capital

Reported in Template C01.00 – Field 020.
"""
    }
]

# ==============================
# RETRIEVAL
# ==============================

def retrieve_context(query: str):

    q = query.lower()
    matches = []

    if any(k in q for k in ["share", "equity", "retained"]):
        matches.append(REGULATORY_RULES[0]["text"])

    if any(k in q for k in ["tier 1", "at1"]):
        matches.append(REGULATORY_RULES[1]["text"])

    if not matches:
        matches.append("No rule matched.")

    return "\n\n".join(matches)

# ==============================
# LLM PROMPT
# ==============================

SYSTEM_PROMPT = """
You are a PRA COREP reporting assistant.

Return ONLY valid JSON.

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

def generate_structured_output(query, context):

    prompt = f"""
Regulatory Context:
{context}

Scenario:
{query}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# ==============================
# TEMPLATE MAPPING
# ==============================

def map_template(data):

    rows = []

    for f in data["fields"]:
        rows.append({
            "Field Code": f["code"],
            "Description": f["label"],
            "Value": f["value"],
            "Rule Source": f["source_rule"]
        })

    return rows

# ==============================
# VALIDATION
# ==============================

def validate(data):

    flags = []

    total_cet1 = sum(
        f["value"]
        for f in data["fields"]
        if f["code"] == "010"
    )

    if total_cet1 <= 0:
        flags.append("CET1 cannot be zero.")

    data["validation_flags"] = flags

    return data

# ==============================
# API
# ==============================

@app.get("/")
def health():
    return {"status": "Backend running"}

@app.post("/report")
def generate_report(query: str = Query(...)):

    context = retrieve_context(query)

    llm_output = generate_structured_output(query, context)

    try:
        structured = json.loads(llm_output)
    except:
        return {
            "error": "Invalid JSON from LLM",
            "raw": llm_output
        }

    structured = validate(structured)

    template = map_template(structured)

    audit_log = context.split("\n\n")

    return {
        "structured_output": structured,
        "template_extract": template,
        "audit_log": audit_log
    }
