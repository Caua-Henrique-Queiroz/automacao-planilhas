import io
import pandas as pd
import streamlit as st


def preparar_excel(df: pd.DataFrame) -> bytes:
    """Return bytes representing an Excel file with a single sheet named 'Lista'.

    This helper is useful whenever we need to generate a downloadable
    spreadsheet from a ``DataFrame``. The caller can pass the resulting
    bytes directly to ``st.download_button``.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Lista")
    return output.getvalue()


def download_button_from_df(
    df: pd.DataFrame,
    label: str,
    file_name: str,
    mime: str = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
) -> None:
    """Create a Streamlit download button for the given dataframe.

    The function centralizes the logic required to prepare the Excel bytes
    and call ``st.download_button`` so that the UI file ``app.py`` can
    remain lean and focused on layout. If ``df`` is empty, nothing is
    rendered.
    """
    if df.empty:
        return

    excel_data = preparar_excel(df)
    st.download_button(
        label=label,
        data=excel_data,
        file_name=file_name,
        mime=mime,
    )