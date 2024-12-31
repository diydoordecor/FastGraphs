import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title and Sidebar
def main():
    st.set_page_config(layout="wide")
    st.title("FastGraphs Dashboard")

    st.sidebar.title("Dashboard Filters")
    
    # Sample data loading
    st.sidebar.markdown("## Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type="csv")
    
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.sidebar.markdown("---")
        st.sidebar.markdown("## Filters")

        # Add filters based on data columns
        column_names = data.columns
        filters = {}
        for column in column_names:
            unique_values = data[column].dropna().unique()
            if len(unique_values) < 20:  # Dropdown for categorical
                selected_values = st.sidebar.multiselect(f"Select {column}", unique_values, unique_values)
                filters[column] = selected_values
            else:  # Slider for numerical values
                if pd.api.types.is_numeric_dtype(data[column]):
                    min_val, max_val = int(data[column].min()), int(data[column].max())
                    selected_range = st.sidebar.slider(f"Select range for {column}", min_val, max_val, (min_val, max_val))
                    filters[column] = selected_range

        # Filter the data based on selections
        for key, value in filters.items():
            if isinstance(value, list):  # Multiselect
                data = data[data[key].isin(value)]
            elif isinstance(value, tuple):  # Slider range
                data = data[(data[key] >= value[0]) & (data[key] <= value[1])]

        # Display filtered data
        st.write("### Filtered Data", data)

        # Visualization options
        st.markdown("---")
        st.markdown("## Visualizations")

        visualization_type = st.selectbox("Choose visualization type", ["Bar Chart", "Line Chart", "Scatter Plot"])

        if st.button("Generate Visualization"):
            if visualization_type == "Bar Chart":
                generate_bar_chart(data)
            elif visualization_type == "Line Chart":
                generate_line_chart(data)
            elif visualization_type == "Scatter Plot":
                generate_scatter_plot(data)

# Visualization Functions
def generate_bar_chart(data):
    st.markdown("### Bar Chart")
    x_column = st.selectbox("Select X-axis", data.columns, key="bar_x")
    y_column = st.selectbox("Select Y-axis", data.columns, key="bar_y")

    if x_column and y_column:
        chart_data = data.groupby(x_column)[y_column].mean().sort_values()
        st.bar_chart(chart_data)

def generate_line_chart(data):
    st.markdown("### Line Chart")
    x_column = st.selectbox("Select X-axis", data.columns, key="line_x")
    y_column = st.selectbox("Select Y-axis", data.columns, key="line_y")

    if x_column and y_column:
        plt.figure(figsize=(10, 5))
        plt.plot(data[x_column], data[y_column])
        plt.title(f"Line Chart: {x_column} vs {y_column}")
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        st.pyplot(plt)

def generate_scatter_plot(data):
    st.markdown("### Scatter Plot")
    x_column = st.selectbox("Select X-axis", data.columns, key="scatter_x")
    y_column = st.selectbox("Select Y-axis", data.columns, key="scatter_y")

    if x_column and y_column:
        plt.figure(figsize=(10, 5))
        plt.scatter(data[x_column], data[y_column], alpha=0.7)
        plt.title(f"Scatter Plot: {x_column} vs {y_column}")
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        st.pyplot(plt)

if __name__ == "__main__":
    main()


