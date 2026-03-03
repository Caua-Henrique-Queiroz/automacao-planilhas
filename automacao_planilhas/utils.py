import io
import pandas as pd


def preparar_excel(df):
    """Return bytes representing an Excel file with a single sheet named 'Lista'."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Lista")
    return output.getvalue()
