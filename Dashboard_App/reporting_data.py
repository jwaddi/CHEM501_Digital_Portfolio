# reporting_data.py
# PDF report generation and data export utilities

import matplotlib.pyplot as plt
from fpdf import FPDF
from PIL import Image
import pandas as pd
import io
import streamlit as st
import matplotlib as mt


def generate_pdf_report(
    option,
    data_dict,
    df_clean,
    compare_variables=None
):
    """
    Generate a PDF report and Streamlit download buttons.
    """

    mt.use("Agg")

    selected_data = data_dict[option]
    col = selected_data.columns[1] if option != "Overview" else None

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 10, f"{option} Report", ln=True, align="C")

    # --------------------------------------------------
    # Raw data table
    # --------------------------------------------------
    if option != "Overview":
        pdf.set_font("Times", "", 12)
        pdf.cell(0, 8, f"Time (s), {option}", ln=True)
        for _, row in selected_data.iterrows():
            pdf.cell(
                0, 5,
                f"{row['Time (s)']}, {row[col]}",
                ln=True
            )

    # --------------------------------------------------
    # Summary statistics
    # --------------------------------------------------
    if option != "Overview":
        pdf.ln(5)
        pdf.set_font("Times", "B", 14)
        pdf.cell(0, 8, "Summary Statistics", ln=True)
        pdf.set_font("Times", "", 12)
        pdf.cell(0, 5, f"Mean: {selected_data[col].mean():.2f}", ln=True)
        pdf.cell(0, 5, f"Max: {selected_data[col].max():.2f}", ln=True)
        pdf.cell(0, 5, f"Min: {selected_data[col].min():.2f}", ln=True)

    # --------------------------------------------------
    # Main plot
    # --------------------------------------------------
    fig, ax = plt.subplots()

    if option == "Overview":
        for c in selected_data.columns[1:]:
            ax.plot(selected_data["Time (s)"], selected_data[c], label=c)
        ax.legend()
    else:
        ax.plot(
            selected_data["Time (s)"],
            selected_data[col],
            marker="o",
            markersize=3
        )

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Values" if option == "Overview" else col)

    fig.savefig("main_plot.png", bbox_inches="tight")
    plt.close(fig)

    _add_image_to_pdf(pdf, "main_plot.png")

    # --------------------------------------------------
    # Comparison plot
    # --------------------------------------------------
    if compare_variables:
        fig2, ax2 = plt.subplots()
        for var in compare_variables:
            df = data_dict[var]
            y_col2 = df.columns[1]
            ax2.plot(
                df["Time (s)"],
                df[y_col2],
                label=var,
                marker="o",
                markersize=3
            )
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Values")
        ax2.legend()

        fig2.savefig("comparison_plot.png", bbox_inches="tight")
        plt.close(fig2)

        pdf.add_page()
        _add_image_to_pdf(pdf, "comparison_plot.png")

    # --------------------------------------------------
    # PDF download
    # --------------------------------------------------
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    pdf_buffer = io.BytesIO(pdf_bytes)

    st.download_button(
        "Download PDF Report",
        data=pdf_buffer,
        file_name=f"{option}_report.pdf",
        mime="application/pdf"
    )

    # --------------------------------------------------
    # CSV
    # --------------------------------------------------
    csv_data = df_clean.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        data=csv_data,
        file_name=f"{option}_cleaned.csv",
        mime="text/csv"
    )

    # --------------------------------------------------
    # Excel
    # --------------------------------------------------
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df_clean.to_excel(writer, index=False)
    excel_buffer.seek(0)

    st.download_button(
        "Download Excel",
        data=excel_buffer,
        file_name=f"{option}_cleaned.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # --------------------------------------------------
    # JSON
    # --------------------------------------------------
    json_data = df_clean.to_json(orient="records")
    st.download_button(
        "Download JSON",
        data=json_data,
        file_name=f"{option}_cleaned.json",
        mime="application/json"
    )


def _add_image_to_pdf(pdf, image_path):
    """
    Helper function to scale and add an image to a PDF page.
    """
    im = Image.open(image_path)
    img_width, img_height = im.size

    max_width = 190
    scale = max_width / img_width
    scaled_height = img_height * scale

    if scaled_height > 277:
        pdf.add_page()

    pdf.image(
        image_path,
        x=10,
        y=pdf.get_y() + 5,
        w=max_width,
        h=scaled_height
    )
