import streamlit as st
import requests
import pandas as pd

# ----------------------------------------
# Page Config
# ----------------------------------------

st.set_page_config(
    page_title="COREP Reporting Assistant",
    page_icon="📊",
    layout="wide"
)

st.title("📊 LLM-Assisted COREP Reporting Assistant")
st.markdown(
    "Prototype — PRA COREP regulatory reporting powered by Groq LLM + RAG"
)

# ----------------------------------------
# Sidebar — Template Selector
# ----------------------------------------

st.sidebar.header("⚙️ Report Settings")

template_option = st.sidebar.selectbox(
    "Select COREP Template",
    [
        "C01.00 — Own Funds",
        "C02.00 — Capital Requirements",
        "C07.00 — Credit Risk"
    ]
)

st.sidebar.info(
    "Prototype currently supports Own Funds logic.\n"
    "Other templates are UI placeholders."
)

# ----------------------------------------
# API Endpoint
# ----------------------------------------

 API_URL = "https://corep-backend.onrender.com/report"



# ----------------------------------------
# Session State (Chat Memory)
# ----------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------------------
# Display Chat History
# ----------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------------------
# Chat Input
# ----------------------------------------

query = st.chat_input(
    "Describe the reporting scenario..."
)

if query:

    st.session_state.messages.append(
        {"role": "user", "content": query}
    )

    with st.chat_message("user"):
        st.markdown(query)

    # ----------------------------------------
    # Call Backend
    # ----------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Analyzing regulations..."):

            try:

                response = requests.post(
                    API_URL,
                    params={"query": query}
                )

                data = response.json()

                if "error" in data:
                    st.error(data["error"])
                    st.stop()

                structured = data["structured_output"]
                template = data["template_extract"]
                audit_log = data["audit_log"]

                # ----------------------------------------
                # Alerts
                # ----------------------------------------
                
                alerts_container = st.container()
                if structured.get("missing_data"):
                    alerts_container.warning(
                        "⚠️ Missing Data Detected: "
                        + ", ".join(structured["missing_data"])
                    )
                
                if structured.get("validation_flags"):
                    alerts_container.error(
                        "🚩 Validation Flags: "
                        + ", ".join(structured["validation_flags"])
                    )

                # Main content layout
                col1, col2 = st.columns(2)

                # ----------------------------------------
                # Column 1: Structured COREP Output
                # ----------------------------------------
                with col1:
                    st.subheader("🧾 Structured COREP Output")
                    
                    for field in structured["fields"]:
                        confidence = field.get("confidence", "High")
                        if confidence == "High":
                            badge_color = "green"
                            badge_text = "High"
                        elif confidence == "Medium":
                            badge_color = "orange"
                            badge_text = "Medium"
                        else:
                            badge_color = "red"
                            badge_text = "Low"

                        with st.container(border=True):
                            st.markdown(f"**{field['label']}**")
                            st.markdown(f"### £{field['value']:,}")
                            
                            sub_col1, sub_col2 = st.columns([1,2])
                            with sub_col1:
                                st.markdown(f":{badge_color}[{badge_text} Confidence]")
                            with sub_col2:
                                st.caption(f"Rule: {field['source_rule']}")


                # ----------------------------------------
                # Column 2: Template Table & Export
                # ----------------------------------------
                with col2:
                    st.subheader("📊 COREP Template Extract")
                    
                    df = pd.DataFrame(template)
                    st.dataframe(
                        df,
                        use_container_width=True
                    )

                    st.download_button(
                        label="⬇️ Download Template CSV",
                        data=df.to_csv(index=False),
                        file_name="corep_template.csv",
                        mime="text/csv"
                    )

                # ----------------------------------------
                # Audit Log (Full Width)
                # ----------------------------------------
                st.subheader("📚 Audit Log (Rule Citations)")
                for i, log in enumerate(audit_log, 1):
                    with st.expander(f"Rule Source {i}"):
                        st.markdown(log)

                # Save assistant message
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "Generated COREP report successfully."
                    }
                )

            except Exception as e:
                st.error(f"API Error: {str(e)}")
