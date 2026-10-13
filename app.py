import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from src.data_loader import load_data
from src.chain_runner import analyze_dataframe

load_dotenv()

st.set_page_config(page_title="LangChain Data Analyzer", layout="wide")
st.title("📊 Automated Data Analysis using LangChain")

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

question = st.text_input("Enter your analysis question:", placeholder="e.g. What is the average tuition cost for master programs?")

if uploaded_file and question:
    try:
        with st.spinner("Reading file..."):
            df = load_data(uploaded_file)
            df.columns = [str(c) for c in df.columns]
        st.success(f"Loaded {len(df)} rows and {len(df.columns)} columns")

        st.write("### Data Preview")
        st.dataframe(df.head())

        with st.spinner("Analyzing..."):
            code, result = analyze_dataframe(df, question)

        st.write("### 🔍 Generated Code")
        st.code(code, language="python")

        st.write("### ✅ Result")
        st.write(result)

    except Exception as e:
        st.error(f"An error occurred: {e}")
