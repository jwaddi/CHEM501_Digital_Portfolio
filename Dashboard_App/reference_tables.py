# reference tables tab

import Dashboard_App as st
import pandas as pd


def render_iaq_reference_table():
    st.subheader("IAQ Reference Table")

    IAQ_table = pd.DataFrame({
        "IAQ Index": ["0-50", "51-100", "101-150", "151-200", "201-250", "251-300", "301+"],
        "Air Quality": [
            "Excellent",
            "Good",
            "Lightly Polluted",
            "Moderately Polluted",
            "Heavily Polluted",
            "Severely Polluted",
            "Extremely Polluted"
        ],
        "Impact": [
            "Pure air; healthy",
            "No irritation or impact on well-being",
            "Reduction of well-being possible",
            "More significant irritation possible",
            "Exposure might lead to effects like headache depending on VOCs",
            "More severe health issues possible if harmful VOCs present",
            "Headaches and additional neurotoxic effects possible"
        ],
        "Suggested Action": [
            "No action required",
            "No action required",
            "Ventilation suggested",
            "Increase ventilation with clean air",
            "Optimize ventilation",
            "Identify contamination and maximize ventilation",
            "Identify contamination, avoid presence, maximize ventilation"
        ]
    })

    row_colors = [
        "#66FF00",  # bright green
        "#61E160",  # green
        "#FFFF00",  # yellow
        "#FFA500",  # orange
        "#FF0000",  # red
        "#800080",  # purple
        "#A52A2A"   # brown
    ]

    def highlight_rows(row):
        return [
            f"background-color: {row_colors[row.name]}; color: black;"
        ] * len(row)

    styled_table = IAQ_table.style.apply(highlight_rows, axis=1)

    st.dataframe(styled_table, use_container_width=True)

    st.write(
        "Source: Indoor Air Quality Index (IAQ) for HVAC applications "
        "(Sorel, accessed November 2025)"
    )
