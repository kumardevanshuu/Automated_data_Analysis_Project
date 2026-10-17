import io

import pandas as pd


def _load_numbers(file_bytes: bytes) -> pd.DataFrame:
    # numbers-parser reads from a file path, so write the upload to a temp file first.
    import os
    import tempfile

    from numbers_parser import Document

    with tempfile.NamedTemporaryFile(suffix=".numbers", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        doc = Document(tmp_path)
        table = doc.sheets[0].tables[0]
        rows = [list(r) for r in table.rows(values_only=True)]
    finally:
        os.remove(tmp_path)

    rows = [r for r in rows if any(v is not None and v != "" for v in r)]
    if len(rows) < 2:
        raise ValueError("The Numbers file needs a header row and at least one data row.")

    # Numbers tables often include empty padding columns; keep only columns with content.
    def _empty(v):
        return v is None or v == ""

    keep = [
        i
        for i in range(len(rows[0]))
        if not _empty(rows[0][i]) or any(not _empty(r[i]) for r in rows[1:])
    ]
    header = [str(rows[0][i]) if not _empty(rows[0][i]) else f"column_{i}" for i in keep]
    body = [[r[i] for i in keep] for r in rows[1:]]
    return pd.DataFrame(body, columns=header)


def load_data(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    if name.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(file_bytes))
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(file_bytes))
    elif name.endswith(".numbers"):
        df = _load_numbers(file_bytes)
    else:
        raise ValueError("Unsupported file type. Upload a CSV, Excel (.xlsx), or Numbers (.numbers) file.")

    df.columns = [str(c) for c in df.columns]
    return df
