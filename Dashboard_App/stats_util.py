# statistics tab

def render_statistics_tab(selected_data, option, y_col):
    if option == "Overview":
        st.info("Summary statistics not available for Overview mode.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mean", selected_data[y_col].mean())
    col2.metric("Max", selected_data[y_col].max())
    col3.metric("Min", selected_data[y_col].min())
    col4.metric("Std Dev", f"{selected_data[y_col].std():.3f}")
