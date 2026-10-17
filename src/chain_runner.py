import ast
import builtins
import os
import re
from typing import Any, Optional, Tuple

import numpy as np
import pandas as pd
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

MODEL_NAME = "openai/gpt-oss-120b"

PROMPT = PromptTemplate(
    input_variables=["dtypes", "sample", "question"],
    template=(
        "You have a pandas DataFrame named df.\n"
        "Columns and data types:\n{dtypes}\n\n"
        "First rows of df:\n{sample}\n\n"
        "Write Python code using pandas to answer this question: '{question}'.\n"
        "Rules:\n"
        "- Store the final answer in a variable named result.\n"
        "- Also store the rows of df that the answer is based on in a variable named "
        "matched_rows. It must be a pandas DataFrame with the original columns. "
        "For a filter question, it holds the filtered rows. For a max, min or count "
        "question, it holds the rows used to get the answer.\n"
        "- Do not modify df. Do not import anything: pandas is available as pd and "
        "numpy as np.\n"
        "- Return only the code, with no explanation."
    ),
)

SAFE_BUILTINS = {
    name: getattr(builtins, name)
    for name in [
        "abs", "all", "any", "bool", "dict", "enumerate", "filter", "float", "int",
        "isinstance", "len", "list", "map", "max", "min", "print", "range", "reversed",
        "round", "set", "sorted", "str", "sum", "tuple", "zip",
    ]
}

BLOCKED_NAMES = {
    "open", "exec", "eval", "compile", "globals", "locals", "vars", "getattr",
    "setattr", "delattr", "input", "breakpoint", "os", "sys", "subprocess", "socket",
    "shutil", "pathlib", "__import__",
}

BLOCKED_ATTRS = {
    "to_csv", "to_excel", "to_pickle", "to_sql", "to_parquet", "to_json", "to_html",
    "to_clipboard", "to_feather", "to_hdf", "to_stata", "to_xml", "to_markdown",
    "to_latex",
}


def extract_code(raw: str) -> str:
    match = re.search(r"```(?:python|py)?\s*\n(.*?)```", raw, re.DOTALL | re.IGNORECASE)
    code = match.group(1) if match else raw
    return code.strip()


def check_code_is_safe(code: str) -> None:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        raise ValueError("The AI did not return valid code. Try rephrasing your question.")

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise ValueError("The generated code tried to import a module, so it was blocked.")
        if isinstance(node, ast.While):
            raise ValueError("The generated code used a while loop, so it was blocked.")
        if isinstance(node, ast.Name) and node.id in BLOCKED_NAMES:
            raise ValueError(f"The generated code used '{node.id}', so it was blocked.")
        if isinstance(node, ast.Attribute):
            if node.attr.startswith("__"):
                raise ValueError("The generated code used a private attribute, so it was blocked.")
            if node.attr.startswith("read_") or node.attr in BLOCKED_ATTRS:
                raise ValueError("The generated code tried to read or write files, so it was blocked.")


def to_row_table(value: Any, df: pd.DataFrame) -> Optional[pd.DataFrame]:
    if isinstance(value, pd.DataFrame):
        return value
    if isinstance(value, pd.Series):
        if len(value) > 0 and all(label in df.columns for label in value.index):
            return value.to_frame().T
        return value.to_frame()
    return None


def run_code(df: pd.DataFrame, code: str) -> Tuple[Any, Optional[pd.DataFrame]]:
    check_code_is_safe(code)

    namespace = {"__builtins__": SAFE_BUILTINS, "df": df.copy(), "pd": pd, "np": np}
    exec(code, namespace)

    if "result" not in namespace:
        raise ValueError("The generated code did not produce a 'result'. Try rephrasing your question.")

    result = namespace["result"]
    matched_rows = to_row_table(namespace.get("matched_rows"), df)
    return result, matched_rows


def generate_code(df: pd.DataFrame, question: str) -> str:
    llm = ChatGroq(
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name=MODEL_NAME,
    )
    chain = PROMPT | llm
    response = chain.invoke({
        "dtypes": df.dtypes.astype(str).to_string(),
        "sample": df.head(3).to_string(max_colwidth=40),
        "question": question,
    })
    return extract_code(response.content)


def analyze_dataframe(df: pd.DataFrame, question: str) -> Tuple[str, Any, Optional[pd.DataFrame]]:
    code = generate_code(df, question)
    result, matched_rows = run_code(df, code)
    return code, result, matched_rows