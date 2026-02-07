                    ┌──────────────────────┐
                    │   Streamlit UI       │
                    │  (Chat Interface)   │
                    └─────────┬────────────┘
                              │
                              │ User Query
                              ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │  Backend Orchestrator│
                    └─────────┬────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼

 ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
 │  RAG Retriever │  │   Groq LLM     │  │ Validation     │
 │ (FAISS +       │  │ Interpretation │  │ Engine         │
 │ Embeddings)    │  │ + Structuring  │  │                │
 └───────┬────────┘  └────────┬───────┘  └────────┬───────┘
         │                    │                   │
         │ Retrieved Rules   │ JSON Output       │ Flags
         ▼                    ▼                   ▼

            ┌────────────────────────────────┐
            │   Field Aggregation Layer      │
            │ (Combine CET1 components etc.)│
            └───────────────┬────────────────┘
                            │
                            ▼
                 ┌────────────────────────┐
                 │ Template Mapper       │
                 │ COREP C01.00 Extract  │
                 └────────────┬──────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │ Structured Output   │
                    │ Template Table      │
                    │ Audit Log           │
                    └──────────────────────┘

The system begins with a Streamlit chat interface where the user submits a regulatory reporting scenario.
The FastAPI backend orchestrates the workflow.
A Retrieval-Augmented Generation layer searches PRA and COREP regulatory texts using vector embeddings.
Retrieved rules are passed to a Groq-hosted LLM, which interprets them and produces structured COREP-aligned JSON output.
A deterministic aggregation and validation layer ensures field consistency.
Finally, the data is mapped into a human-readable COREP template extract with an accompanying audit trail.