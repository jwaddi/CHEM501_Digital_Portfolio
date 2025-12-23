# theme_toggle.py
# Handles light/dark theme switching for Streamlit + matplotlib

import streamlit as st
import matplotlib as mt

def theme_selector():
    """
    Render theme selector in sidebar and return selected theme.
    """
    return st.sidebar.radio(
        "Theme",
        ["Dark", "Light"],
        index=0
    )


def apply_theme(theme):
    """
    Apply theme styles to matplotlib and Streamlit via CSS.
    """
    if theme == "Dark":
        # Matplotlib dark styling
        mt.rcParams.update({
            "axes.facecolor": "#222222",
            "figure.facecolor": "#222222",
            "savefig.facecolor": "#222222",
            "axes.edgecolor": "#E7E8CB",
            "axes.labelcolor": "#E7E8CB",
            "xtick.color": "#E7E8CB",
            "ytick.color": "#E7E8CB",
            "text.color": "#E7E8CB",
            "legend.facecolor": "#333333",
            "grid.color": "#444444"
        })

        # Streamlit dark CSS
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #111111;
                color: #E7E8CB;
            }
            .stSidebar {
                background-color: #121212;
                color: #E7E8CB;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    else:
        # Matplotlib light styling
        mt.rcParams.update({
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.edgecolor": "black",
            "axes.labelcolor": "black",
            "xtick.color": "black",
            "ytick.color": "black",
            "text.color": "black",
            "legend.facecolor": "#FFFFFF",
            "grid.color": "#DDDDDD"
        })

        # HARD reset to override config.toml dark theme
        st.markdown(
            """
            <style>
            html, body, .stApp, [class^="st-"], [class*=" st-"] {
                background-color: white !important;
                color: black !important;
            }

            .stSidebar {
                background-color: #F8F8F8 !important;
                color: black !important;
            }

            input, textarea, select, button {
                background-color: white !important;
                color: black !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
