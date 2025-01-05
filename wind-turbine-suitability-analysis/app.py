import streamlit as st
import pandas as pd
import plotly.express as px
import json
import numpy as np

# Set Streamlit page configuration
st.set_page_config(page_title="Wind Turbine Suitability Dashboard", layout="wide")

# Load JSON data
with open("data/coordinates.json", "r") as f:
    data = json.load(f)

# Convert JSON list into a DataFrame
df = pd.DataFrame(data, columns=["Longitude", "Latitude"])

# Add random suitability scores and parameters for demonstration
df["Suitability Score"] = np.random.uniform(1, 10, size=len(df))
df["Wind Speed"] = np.random.uniform(3, 12, size=len(df))  # Wind speed in m/s
df["Elevation"] = np.random.uniform(50, 300, size=len(df))  # Elevation in meters
df["Slope"] = np.random.uniform(0, 20, size=len(df))  # Slope in degrees

# Add random provinces for filtering (replace with actual province data if available)
province = [
    "Eastern Cape"
]
df["Province"] = np.random.choice(province, size=len(df))

# Streamlit App Layout
st.title("Interactive Wind Turbine Suitability Dashboard")
st.markdown("""
This dashboard visualizes potential wind turbine locations based on suitability scores and other key parameters.
Use the filters to interact with the map and explore important metrics.
""")

# Sidebar Filters
st.sidebar.header("Filters")

# Province Filter
selected_province = st.sidebar.selectbox(
    "Select a Province",
    options=["None"] + province,
)

# Suitability Score Filter
min_score = st.sidebar.slider(
    "Minimum Suitability Score",
    min_value=float(df["Suitability Score"].min()),
    max_value=float(df["Suitability Score"].max()),
    value=float(df["Suitability Score"].min()),
)

# Filter by Contributing Factor
st.sidebar.header("Filter by Contributing Factors")
factor = st.sidebar.selectbox(
    "Select Factor to Filter",
    options=["None", "Wind Speed", "Elevation", "Slope"]
)

# Threshold Slider for the Selected Factor
threshold = None
if factor != "None":
    threshold = st.sidebar.slider(
        f"Minimum {factor}",
        min_value=float(df[factor].min()),
        max_value=float(df[factor].max()),
        value=float(df[factor].min()),
    )

# Apply Filters to the Dataset
filtered_data = df[df["Suitability Score"] >= min_score]

# Apply Province Filter
if selected_province != " ":
    filtered_data = filtered_data[filtered_data["Province"] == selected_province]

# Apply Factor Filter
if factor != "None" and threshold is not None:
    filtered_data = filtered_data[filtered_data[factor] >= threshold]

# Display Cards for Key Metrics
st.subheader("Key Parameters")
col1, col2, col3, col4 = st.columns(4)

# Cards for averages
if not filtered_data.empty:
    col1.metric("Average Wind Speed (m/s)", round(filtered_data["Wind Speed"].mean(), 2))
    col2.metric("Average Elevation (m)", round(filtered_data["Elevation"].mean(), 2))
    col3.metric("Average Slope (°)", round(filtered_data["Slope"].mean(), 2))
    col4.metric("Average Suitability Score", round(filtered_data["Suitability Score"].mean(), 2))

    # Identify the most influential parameter (highest average)
    influential_param = filtered_data[["Wind Speed", "Elevation", "Slope"]].mean().idxmax()
    st.info(f"The most influential parameter is: **{influential_param}**.")
else:
    col1.metric("Average Wind Speed (m/s)", "N/A")
    col2.metric("Average Elevation (m)", "N/A")
    col3.metric("Average Slope (°)", "N/A")
    col4.metric("Average Suitability Score", "N/A")
    st.info("No data available for selected filters.")

# Map Visualization
st.subheader("Filtered Wind Turbine Site Locations")
if not filtered_data.empty:
    fig = px.scatter_mapbox(
        filtered_data,
        lat="Latitude",
        lon="Longitude",
        size="Suitability Score",
        color="Suitability Score",
        color_continuous_scale="Viridis",
        size_max=15,
        zoom=5,
        mapbox_style="carto-positron",
        title="Wind Turbine Site Suitability Map",
        hover_data={"Latitude": True, "Longitude": True, "Suitability Score": True, "Province": True},
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("No sites match the selected criteria.")

# Bar Chart Comparing Averages Across Provinces
st.subheader("Comparison of Key Parameters Across Province")
province_avg = df.groupby("Province")[["Wind Speed", "Elevation", "Slope", "Suitability Score"]].mean().reset_index()
fig_bar = px.bar(
    province_avg,
    x="Province",
    y=["Wind Speed", "Elevation", "Slope", "Suitability Score"],
    barmode="group",
    title="Average Key Parameters by Province",
    labels={"value": "Average Value", "variable": "Parameter"},
)
st.plotly_chart(fig_bar, use_container_width=True)

# Download Filtered Data
st.subheader("Download Filtered Data")
csv = filtered_data.to_csv(index=False)
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name="filtered_suitable_sites.csv",
    mime="text/csv",
)
