import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="IS 445 HW6 | License Explorer", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/UIUC-iSchool-DataViz/is445_data/main/licenses_fall2022.csv"

@st.cache_data
def load_data():
    records = pd.read_csv(DATA_URL, low_memory=False)
    records = records.dropna(subset=["License Type", "License Status"]).copy()
    records["Issue Year"] = pd.to_datetime(
        records["Original Issue Date"], errors="coerce"
    ).dt.year
    return records

st.title("Illinois Professional Licenses: Status and Issue-Year Patterns")
st.write(
    "**IS 445 — Homework 6.** This interactive report explores a sample of "
    "Illinois professional-license records using two different visualizations. "
    "Use the sidebar to filter the records."
)

try:
    df = load_data()
except Exception as error:
    st.error(f"Could not load the public dataset: {error}")
    st.stop()

status_choices = sorted(df["License Status"].unique().tolist())
default_statuses = df["License Status"].value_counts().head(4).index.tolist()
st.sidebar.header("Explore the data")
selected_statuses = st.sidebar.multiselect(
    "License status (changes both charts)",
    options=status_choices,
    default=default_statuses,
)
if not selected_statuses:
    st.warning("Select at least one license status in the sidebar.")
    st.stop()
filtered = df[df["License Status"].isin(selected_statuses)].copy()

st.header("1. License types and their status composition")
top_types = filtered["License Type"].value_counts().head(10).index.tolist()
bar_data = (
    filtered[filtered["License Type"].isin(top_types)]
    .groupby(["License Type", "License Status"])
    .size()
    .reset_index(name="Records")
)
chart1 = (
    alt.Chart(bar_data)
    .mark_bar()
    .encode(
        x=alt.X("Records:Q", title="Number of records"),
        y=alt.Y("License Type:N", sort=top_types, title="License type"),
        color=alt.Color("License Status:N", title="License status"),
        tooltip=[
            alt.Tooltip("License Type:N"),
            alt.Tooltip("License Status:N"),
            alt.Tooltip("Records:Q", format=","),
        ],
    )
    .properties(height=410, title="Ten most frequent license types in the selection")
)
st.altair_chart(chart1, use_container_width=True)
st.markdown(
    "**Visualization 1 — design and interpretation.** This stacked horizontal "
    "bar chart compares record counts across the ten most frequent license "
    "types in the selected subset. Bar length encodes the number of records, "
    "while distinct colors encode license status. Horizontal bars make "
    "category names easier to read, and stacking reveals each type's status "
    "composition. Filtering statuses from the sidebar changes the counts "
    "and types shown, helping viewers explore differences across categories."
)

st.divider()
st.header("2. Changes in recorded original issue years")
issued = filtered.dropna(subset=["Issue Year"]).copy()
if issued.empty:
    st.info("No valid original issue dates are available for this selection.")
else:
    earliest = int(issued["Issue Year"].min())
    latest = int(issued["Issue Year"].max())
    if earliest < latest:
        year_range = st.sidebar.slider(
            "Original issue-year range (changes chart 2)",
            min_value=earliest,
            max_value=latest,
            value=(max(earliest, 1990), latest),
        )
    else:
        year_range = (earliest, latest)
    selected_years = issued[
        issued["Issue Year"].between(year_range[0], year_range[1])
    ].copy()
    top_five = selected_years["License Type"].value_counts().head(5).index.tolist()
    area_data = (
        selected_years[selected_years["License Type"].isin(top_five)]
        .groupby(["Issue Year", "License Type"])
        .size()
        .reset_index(name="Records")
    )
    chart2 = (
        alt.Chart(area_data)
        .mark_area(opacity=0.85)
        .encode(
            x=alt.X("Issue Year:O", title="Original issue year"),
            y=alt.Y("Records:Q", title="Number of records"),
            color=alt.Color("License Type:N", title="License type"),
            tooltip=[
                alt.Tooltip("Issue Year:O", title="Year"),
                alt.Tooltip("License Type:N"),
                alt.Tooltip("Records:Q", format=","),
            ],
        )
        .properties(height=360, title="Issue-year distribution for five frequent license types")
    )
    st.altair_chart(chart2, use_container_width=True)
    st.markdown(
        "**Visualization 2 — design and interpretation.** This stacked area "
        "chart shows how records are distributed by original issue year for "
        "five frequent license types within the selected period. Horizontal "
        "position encodes year, vertical height encodes record count, and "
        "colors distinguish types. Stacked areas show changes in both overall "
        "counts and the category mix. The year-range slider lets viewers "
        "focus on different periods beyond standard zoom or tooltips."
    )

st.divider()
st.subheader("Data source and limitations")
st.markdown(
    "[UIUC iSchool — licenses_fall2022.csv]("
    "https://github.com/UIUC-iSchool-DataViz/is445_data/blob/main/licenses_fall2022.csv)"
)
st.caption(
    "Only aggregated counts are shown. This provided dataset is not a verified "
    "census of Illinois licenses; the charts describe these records only. "
    "Original issue year is not the year a license necessarily became active. "
    "Both charts were developed for HW6 rather than copied from HW5."
)
