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
    version="2.0"
)

# ==============================
# REGULATORY CORPUS
# ==============================

REGULATORY_RULES = {
    "C01.00": [
        {
            "id": "Article 26",
            "text": """
Article 26 – Common Equity Tier 1 Capital

Includes:
(a) Ordinary share capital
(b) Retained earnings

Report under COREP Template C01.00 Field 010.
"""
        },
        {
            "id": "Article 51",
            "text": """
Article 51 – Additional Tier 1 Capital

Includes perpetual subordinated instruments.

Report under Template C01.00 Field 020.
"""
        }
    ],

    "C02.00": [
        {
            "id": "Article 92",
            "text": """
Article 92 – Capital Requirements

Institutions must maintain minimum capital ratios
against risk-weighted assets.

Reported under COREP Template C02.00.
"""
        }
    ]
}

# ==============================
# RETRIEVAL
# ==============================

def retrieve_context(template, query):

    rules = REGULATORY_RULES.get(template, [])
    return "\n\n".join(rule["text"] for rule in rules)


# ==============================
# LLM PROMPT
# ==============================

SYSTEM_PROMPT = """
You are a PRA COREP regulatory reporting assistant.

Return ONLY valid JSON.

Schema:

{
  "template": "string",
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


def generate_structured_output(query, template, context):

    prompt = f"""
Template: {template}

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

def map_to_template(structured_json):

    rows = []

    for field in structured_json["fields"]:
        rows.append({
            "Field Code": field["code"],
            "Description": field["label"],
            "Value": field["value"],
            "Rule Source": field["source_rule"]
        })

    return rows


# ==============================
# VALIDATION
# ==============================

def run_validations(data):

    flags = []

    cet1_total = sum(
        f["value"]
        for f in data["fields"]
        if f["code"] == "010"
    )

    if cet1_total <= 0:
        flags.append("CET1 capital cannot be zero or negative.")

    data["validation_flags"] = flags

    return data


# ==============================
# API ENDPOINT
# ==============================

@app.post("/report")
def generate_report(
    query: str = Query(...),
    template: str = Query("C01.00")
):

    context = retrieve_context(template, query)

    llm_output = generate_structured_output(
        query, template, context
    )

    try:
        structured_json = json.loads(llm_output)
    except:
        return {
            "error": "Invalid JSON from LLM",
            "raw_output": llm_output
        }

    structured_json = run_validations(structured_json)

    template_extract = map_to_template(structured_json)

    audit_log = context.split("\n\n")

    return {
        "structured_output": structured_json,
        "template_extract": template_extract,
        "audit_log": audit_log
    }


# ==============================
# HEALTH CHECK
# ==============================

@app.get("/")
def root():
    return {"status": "COREP backend running"}
