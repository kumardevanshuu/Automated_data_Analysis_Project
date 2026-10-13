import os
import re
import pandas as pd
from typing import Tuple, Any
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq


def analyze_dataframe(df: pd.DataFrame, question: str) -> Tuple[str, Any]:
    llm = ChatGroq(
    temperature=0,
    groq_api_key=os.getenv('GROQ_API_KEY'),
    model_name="openai/gpt-oss-120b"
    )

    prompt = PromptTemplate(
        input_variables=["columns", "question"],
        template=(
            "You have a pandas DataFrame named df with columns: {columns}.\n"
            "Write Python code using pandas to answer this question: '{question}'.\n"
            "Store the answer in a variable named 'result'.\n"
            "Do NOT modify the DataFrame.\n"
            "Return only executable code."
        )
    )

    # Modern LCEL syntax — replaces deprecated LLMChain
    chain = prompt | llm
    response = chain.invoke({
        "columns": ", ".join(df.columns),
        "question": question
    })

    raw = response.content  # AIMessage.content instead of dict["text"]

    code_lines = []
    for line in raw.splitlines():
        if re.match(r"\s*(result|df|import|from)\b", line):
            code_lines.append(line)
        elif code_lines and (line.startswith(" ") or line.startswith("\t")):
            code_lines.append(line)
    code = "\n".join(code_lines)

    exec_globals = {"df": df, "pd": pd}
    exec_locals = {}
    exec(code, exec_globals, exec_locals)
    result = exec_globals.get("result", exec_locals.get("result"))

    return code, result