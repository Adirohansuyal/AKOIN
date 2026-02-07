import streamlit as st
import requests
import pandas as pd

# ==============================
# CONFIG
# ==============================

API_URL = "https://YOUR-BACKEND.onrender.com/report"

st.set_page_config(
    page_title="COREP Assistant",
    layout="wide"
)

st.title("📊 PRA COREP Reporting Assistant")

# ==============================
# TEMPLATE DROPDOWN
# ==============================

template_choice = st.selectbox(
    "Select COREP Template",
    [
        "C01.00 – Own Funds",
        "C02.00 – Capital Requirements"
    ]
)

template_map = {
    "C01.00 – Own Funds": "C01.00",
    "C02.00 – Capital Requirements": "C02.00"
}

selected_template = template_map[template_choice]

# ==============================
# USER INPUT
# ==============================

query = st.text_area(
    "Describe reporting scenario",
    height=150,
    value="We issued 50 million in shares and retained 10 million earnings."
)

# ==============================
# GENERATE REPORT
# ==============================

if st.button("Generate Report"):

    with st.spinner("Analyzing regulatory scenario..."):

        response = requests.post(
            API_URL,
            params={
                "query": query,
                "template": selected_template
            }
        )

        data = response.json()

    # ==============================
    # STRUCTURED OUTPUT
    # ==============================

    st.subheader("Structured Output")

    st.json(data["structured_output"])

    # ==============================
    # TEMPLATE TABLE
    # ==============================

    st.subheader("COREP Template Extract")

    df = pd.DataFrame(data["template_extract"])

    st.dataframe(df, use_container_width=True)

    # Export button
    st.download_button(
        "Download Template CSV",
        df.to_csv(index=False),
        "corep_template.csv"
    )

    # ==============================
    # VALIDATION ALERTS
    # ==============================

    flags = data["structured_output"]["validation_flags"]

    if flags:
        st.error("⚠ Validation Issues Detected")
        for flag in flags:
            st.write(flag)
    else:
        st.success("✅ No validation issues detected")

    # ==============================
    # AUDIT LOG
    # ==============================

    st.subheader("Audit Log")

    for log in data["audit_log"]:
        st.info(log)
