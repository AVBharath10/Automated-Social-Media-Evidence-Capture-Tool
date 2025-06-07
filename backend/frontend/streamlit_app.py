import streamlit as st
import requests

st.title("Social Media Report Generator")

platform = st.selectbox("Choose Platform", ["instagram", "twitter"])
username = st.text_input(f"{platform.capitalize()} Username")
password = st.text_input(f"{platform.capitalize()} Password", type="password")

if st.button("Generate Report"):
    if not username or not password:
        st.error("Please enter username and password")
    else:
        backend_url = "http://localhost:5000/generate-report"
        with st.spinner("Generating report..."):
            try:
                response = requests.post(backend_url, json={
                    "platform": platform,
                    "username": username,
                    "password": password,
                })
                data = response.json()
                if response.ok:
                    pdf_url = data.get("pdf_url")
                    st.success("Report generated! Download below:")
                    st.markdown(f"[⬇ Download PDF]({pdf_url})")
                else:
                    st.error(f"Error: {data.get('error')}")
            except Exception as e:
                st.error(f"Request failed: {e}")
