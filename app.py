from fastapi import FastAPI, Query
from pydantic import BaseModel
import json
import os
from groq import Groq

# ==============================
# GROQ CLIENT
# ==============================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")  # Render env var
)

# ==============================
# FASTAPI INIT
# ==============================

app = FastAPI(
    title="COREP Reporting Assistant",
    version="1.0"
)

# ==============================
# LIGHTWEIGHT REGULATORY CORPUS
# ==============================

REGULATORY_RULES = [
    {
        "id": "Article 26",
        "text": """
        Article 26 – Common Equity Tier 1 Capital (CET1)

        CET1 includes:

        (a) Ordinary share capital
        (b) Retained earnings
        (c) Accumulated other comprehensive income

        Report under COREP Template C01.00 – Field 010.
        """
    },
    {
        "id": "Article 51",
        "text": """
        Article 51 – Additional Tier 1 Capital (AT1)

        AT1 includes perpetual subordinated instruments
        and hybrid capital instruments.

        Report under Template C01.00 – Field 020.
        """
    }
]

# ==============================
# SIMPLE KEYWORD RETRIEVAL
# ==============================

def retrieve_context(query: str):

    query_lower = query.lower()
    matched_rules = []

    for rule in REGULATORY_RULES:
        if any(keyword in query_lower for keyword in [
            "share", "equity", "cet1", "retained", "capital"
        ]):
            if "26" in rule["id"]:
                matched_rules.append(rule["text"])

        if any(keyword in query_lower for keyword in [
            "tier 1", "at1", "hybrid"
        ]):
            if "51" in rule["id"]:
                matched_rules.append(rule["text"])

    if not matched_rules:
        matched_rules.append("No specific regulatory rule matched.")

    return "\n\n".join(matched_rules)

# ==============================
# LLM PROMPT
# ==============================

SYSTEM_PROMPT = """
You are a PRA COREP regulatory reporting assistant.

Return ONLY valid JSON.

No explanations.
No markdown.

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

# ==============================
# LLM CALL
# ==============================

def generate_structured_output(query, context):

    prompt = f"""
Regulatory Context:
{context}

Reporting Scenario:
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

    template_rows = []

    for field in structured_json["fields"]:
        template_rows.append({
            "Field Code": field["code"],
            "Description": field["label"],
            "Value": field["value"],
            "Rule Source": field["source_rule"]
        })

    return template_rows

# ==============================
# VALIDATION ENGINE
# ==============================

def run_validations(structured_json):

    flags = []

    cet1_total = sum(
        f["value"]
        for f in structured_json["fields"]
        if f["code"] == "010"
    )

    if cet1_total <= 0:
        flags.append("CET1 capital cannot be zero or negative.")

    structured_json["validation_flags"] = flags

    return structured_json

# ==============================
# API ENDPOINT
# ==============================

@app.post("/report")
def generate_report(query: str = Query(...)):

    # 1️⃣ Retrieve regulatory context
    context = retrieve_context(query)

    # 2️⃣ LLM structured output
    llm_output = generate_structured_output(query, context)

    try:
        structured_json = json.loads(llm_output)
    except:
        return {
            "error": "LLM did not return valid JSON",
            "raw_output": llm_output
        }

    # 3️⃣ Validation
    structured_json = run_validations(structured_json)

    # 4️⃣ Template mapping
    template_extract = map_to_template(structured_json)

    # 5️⃣ Audit log
    audit_log = context.split("\n\n")

    return {
        "structured_output": structured_json,
        "template_extract": template_extract,
        "audit_log": audit_log
    }
