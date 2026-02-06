from fastapi import FastAPI
from rag import RAGEngine
from llm import generate_structured_output
from validation import validate_corep
from template_mapper import map_to_template
from aggregator import aggregate_fields

import json

app = FastAPI(
    title="LLM-Assisted COREP Reporting Assistant",
    description="Prototype for PRA COREP regulatory reporting automation",
    version="1.0"
)

# Initialize RAG engine
rag = RAGEngine("data/regulatory_text.txt")


# 🔒 Safe JSON parser
def safe_json_loads(text: str):
    """
    Extracts JSON safely from LLM output.
    Handles markdown, text wrapping, etc.
    """

    if not text:
        raise ValueError("LLM returned empty output")

    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError(f"No JSON found in LLM output:\n{text}")

    json_text = text[start:end]

    return json.loads(json_text)


@app.get("/")
def root():
    return {
        "message": "COREP Reporting Assistant is running 🚀"
    }


@app.post("/report")
def generate_report(query: str):

    try:

        print("\n==============================")
        print("📩 NEW REPORT REQUEST")
        print("==============================")
        print("User Query:\n", query)

        # --------------------------------------------------
        # Step 1 — Retrieve regulatory rules (RAG)
        # --------------------------------------------------
        retrieved_chunks = rag.retrieve(query)

        context = "\n".join(retrieved_chunks)

        print("\n📚 Retrieved Regulatory Context:\n")
        for i, chunk in enumerate(retrieved_chunks, 1):
            print(f"\n--- Chunk {i} ---\n{chunk}")

        # --------------------------------------------------
        # Step 2 — LLM Structured Generation
        # --------------------------------------------------
        llm_output = generate_structured_output(query, context)

        print("\n🤖 LLM RAW OUTPUT:\n")
        print(llm_output)

        # --------------------------------------------------
        # Step 3 — Safe JSON Parsing
        # --------------------------------------------------
        data = safe_json_loads(llm_output)

        print("\n🧾 Parsed Structured JSON:\n", data)

        # --------------------------------------------------
        # Step 4 — Aggregate duplicate COREP fields
        # --------------------------------------------------
        data = aggregate_fields(data)

        print("\n🧮 Aggregated Fields:\n", data["fields"])

        # --------------------------------------------------
        # Step 5 — Validation Rules
        # --------------------------------------------------
        validated_data = validate_corep(data)

        print("\n✅ Validation Flags:\n", validated_data["validation_flags"])

        # --------------------------------------------------
        # Step 6 — Map to Template Extract
        # --------------------------------------------------
        template_df = map_to_template(validated_data)

        template_records = template_df.to_dict(orient="records")

        print("\n📊 Template Extract:\n", template_records)

        # --------------------------------------------------
        # Final Response
        # --------------------------------------------------
        return {
            "structured_output": validated_data,
            "template_extract": template_records,
            "audit_log": retrieved_chunks
        }

    except Exception as e:

        print("\n❌ ERROR OCCURRED:\n", str(e))

        return {
            "error": str(e),
            "hint": "Check terminal logs for LLM output / JSON formatting issues"
        }
