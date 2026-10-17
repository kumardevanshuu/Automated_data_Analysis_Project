import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.chain_runner import analyze_dataframe
from src.data_loader import load_data

load_dotenv()

MAX_ROWS_SHOWN = 500

st.set_page_config(page_title="LangChain Data Analyzer", layout="wide")
st.title("📊 Automated Data Analysis using LangChain")

uploaded_file = st.file_uploader(
    "Upload your CSV, Excel or Numbers file", type=["csv", "xlsx", "numbers"]
)

question = st.text_input(
    "Enter your analysis question:",
    placeholder="e.g. Show all master programs in the USA with tuition above 50000",
)

if uploaded_file and question:
    try:
        with st.spinner("Reading file..."):
            df = load_data(uploaded_file)
            df.columns = [str(c) for c in df.columns]
        st.success(f"Loaded {len(df)} rows and {len(df.columns)} columns")

        st.write("### Data Preview")
        st.dataframe(df.head())

        with st.spinner("Analyzing..."):
            code, result, matched_rows = analyze_dataframe(df, question)

        result_is_the_rows = (
            isinstance(result, pd.DataFrame)
            and matched_rows is not None
            and result.equals(matched_rows)
        )

        st.write("### ✅ Result")
        if result_is_the_rows:
            st.write(f"Found {len(result):,} matching row(s). See the table below.")
        else:
            st.write(result)

        st.write("### 📋 Matching rows from your file")
        if matched_rows is None:
            st.info("The AI did not return the rows behind this answer. Try rephrasing your question.")
        elif matched_rows.empty:
            st.info("No rows in your file matched this question.")
        else:
            total = len(matched_rows)
            if total > MAX_ROWS_SHOWN:
                st.caption(f"{total:,} matching rows. Showing the first {MAX_ROWS_SHOWN}.")
            else:
                st.caption(f"{total:,} matching row(s).")
            st.dataframe(matched_rows.head(MAX_ROWS_SHOWN))
            st.download_button(
                "Download matching rows (CSV)",
                matched_rows.to_csv(index=False).encode("utf-8"),
                file_name="matching_rows.csv",
                mime="text/csv",
            )

        st.write("### 🔍 Generated Code")
        st.code(code, language="python")

    except Exception as e:
        st.error(f"An error occurred: {e}")