# streamlit_app.py
# 📊 AURA Phase 1 - Learning Engine Demo UI

import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="AURA Learning Engine", layout="wide")
st.title("🧠 AURA - Architectural AI Learning Engine (Phase 1)")
st.markdown("""
Welcome to AURA's foundational brain testing interface.
Here you can:
- Upload a real architectural floor plan (JSON format)
- Run structural understanding
- Evaluate rule violations
- Simulate AI design improvement
""")

API_URL = os.getenv("AURA_API_URL", "http://localhost:5000")

# === File Upload ===
st.header("📂 Upload Floor Plan (Parsed JSON)")
uploaded_file = st.file_uploader("Upload JSON file", type=["json"])

if uploaded_file is not None:
    try:
        plan_data = json.load(uploaded_file)
        st.success("✅ Plan loaded successfully!")
        st.json(plan_data)

        # Analyze Button
        if st.button("🧠 Analyze with AURA Engine"):
            with st.spinner("Analyzing floor plan with architectural intelligence..."):
                response = requests.post(f"{API_URL}/analyze", json=plan_data)
                if response.status_code == 200:
                    result = response.json()
                    st.subheader("🧬 Graph Intelligence")
                    st.json(result.get("graph", {}))

                    st.subheader("⚠️ Rule Violations")
                    if result.get("violations"):
                        for v in result["violations"]:
                            st.error(v)
                    else:
                        st.success("✅ No rule violations found.")

                    st.subheader("🔁 Suggested Improvements")
                    st.json(result.get("suggestions", {}))
                else:
                    st.error(f"❌ API Error: {response.status_code}")

    except json.JSONDecodeError:
        st.error("Invalid JSON format. Please upload a valid parsed floor plan.")
else:
    st.info("Awaiting a floor plan upload to begin analysis.")

st.markdown("---")
st.caption("AURA - Built to Disrupt Architecture Like Tesla Disrupted Cars 🚀")
