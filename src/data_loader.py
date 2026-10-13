import pandas as pd

def load_data(file) -> pd.DataFrame:
    if isinstance(file, str): 
        if file.endswith(".csv"):
            return pd.read_csv(file)
        elif file.endswith((".xls", ".xlsx")):
            return pd.read_excel(file)
    else:  
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        elif file.name.endswith((".xls", ".xlsx")):
            return pd.read_excel(file)

    raise ValueError("Unsupported file format. Use .csv or .xlsx")

