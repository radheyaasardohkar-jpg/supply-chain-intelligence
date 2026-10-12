
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data" / "processed"

st.set_page_config(
    page_title="Supply Chain Intelligence Platform",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📦 Supply Chain Intelligence Platform")
st.markdown(
    "Monitor retail sales, inventory health, demand forecasts, "
    "and replenishment risk."
)

st.caption("Retail analytics and demand planning dashboard")

# --------------------------------------------------
# 2. DATA FILES
# --------------------------------------------------

FILES = {
    "category": DATA_DIR / "category_performance.csv",
    "daily": DATA_DIR / "daily_performance.csv",
    "baseline": DATA_DIR / "baseline_forecast.csv",
    "moving": DATA_DIR / "moving_average_forecast.csv",
    "risk": DATA_DIR / "inventory_risk_report.csv",
}


@st.cache_data
def load_csv(path_string):
    return pd.read_csv(path_string)


missing_files = [
    name
    for name, path in FILES.items()
    if not path.exists()
]

if missing_files:
    st.error("The following reports are missing:")
    for name in missing_files:
        st.write(f"- {name}: {FILES[name]}")

    st.info(
        "Run the relevant report scripts from the project root, "
        "then refresh this dashboard."
    )
    st.stop()


category = load_csv(str(FILES["category"]))
daily = load_csv(str(FILES["daily"]))
baseline = load_csv(str(FILES["baseline"]))
moving = load_csv(str(FILES["moving"]))
risk = load_csv(str(FILES["risk"]))

# --------------------------------------------------
# 3. DATA PREPARATION
# --------------------------------------------------

daily["Date"] = pd.to_datetime(daily["Date"], errors="coerce")

for frame in [baseline, moving]:
    if "Date" in frame.columns:
        frame["Date"] = pd.to_datetime(
            frame["Date"], errors="coerce"
        )

    for column in [
        "Units Sold",
        "Baseline Forecast",
        "Moving Average Forecast",
    ]:
        if column in frame.columns:
            frame[column] = pd.to_numeric(
                frame[column], errors="coerce"
            )

for column in [
    "total_units_sold",
    "average_units_sold",
    "average_inventory",
    "average_price",
]:
    if column in category.columns:
        category[column] = pd.to_numeric(
            category[column], errors="coerce"
        )

for column in [
    "total_units_sold",
    "total_units_ordered",
    "average_inventory",
    "average_demand_forecast",
]:
    if column in daily.columns:
        daily[column] = pd.to_numeric(
            daily[column], errors="coerce"
        )

if "Stock Cover Days" in risk.columns:
    risk["Stock Cover Days"] = pd.to_numeric(
        risk["Stock Cover Days"], errors="coerce"
    )

if "Inventory Level" in risk.columns:
    risk["Inventory Level"] = pd.to_numeric(
        risk["Inventory Level"], errors="coerce"
    )

# --------------------------------------------------
# 4. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.title("Dashboard Controls")

categories = sorted(
    category["Category"].dropna().unique().tolist()
)

selected_categories = st.sidebar.multiselect(
    "Product categories",
    options=categories,
    default=categories,
)

filtered_category = category[
    category["Category"].isin(selected_categories)
].copy()

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data source: processed retail inventory CSV reports"
)

if filtered_category.empty:
    st.warning("Select at least one category in the sidebar.")
    st.stop()

# --------------------------------------------------
# 5. EXECUTIVE SUMMARY
# --------------------------------------------------

st.header("Executive Summary")

total_units = filtered_category["total_units_sold"].sum()
average_inventory = filtered_category["average_inventory"].mean()
average_price = filtered_category["average_price"].mean()

critical_count = int(
    (risk["Risk Status"] == "Critical").sum()
)
reorder_count = int(
    (risk["Risk Status"] == "Reorder soon").sum()
)
healthy_count = int(
    (risk["Risk Status"] == "Healthy").sum()
)

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Units Sold",
    f"{total_units:,.0f}",
)

k2.metric(
    "Average Inventory",
    f"{average_inventory:,.1f}",
)

k3.metric(
    "Critical Inventory Pairs",
    f"{critical_count:,}",
)

k4.metric(
    "Reorder Soon",
    f"{reorder_count:,}",
)

st.caption(
    f"Average listed price: {average_price:,.2f} "
    "(price units follow the source dataset)."
)

st.divider()

# --------------------------------------------------
# 6. CATEGORY PERFORMANCE
# --------------------------------------------------

st.header("Category Performance")

left, right = st.columns(2)

with left:
    category_sorted = filtered_category.sort_values(
        "total_units_sold", ascending=False
    )

    fig = px.bar(
        category_sorted,
        x="Category",
        y="total_units_sold",
        color="Category",
        title="Total Units Sold by Category",
        labels={
            "Category": "Product Category",
            "total_units_sold": "Units Sold",
        },
    )

    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.bar(
        filtered_category.sort_values("average_inventory"),
        x="Category",
        y="average_inventory",
        color="Category",
        title="Average Inventory by Category",
        labels={
            "Category": "Product Category",
            "average_inventory": "Average Inventory",
        },
    )

    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with st.expander("View category performance data"):
    st.dataframe(
        filtered_category,
        use_container_width=True,
        hide_index=True,
    )

# --------------------------------------------------
# 7. DAILY SALES TRENDS
# --------------------------------------------------

st.divider()
st.header("Daily Sales and Inventory Trends")

daily = daily.dropna(subset=["Date"]).sort_values("Date")

if not daily.empty:
    min_date = daily["Date"].min().date()
    max_date = daily["Date"].max().date()

    date_range = st.date_input(
        "Select reporting date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="daily_date_range",
    )

    if isinstance(date_range, (tuple, list)):
        if len(date_range) == 2:
            start_date, end_date = date_range
        elif len(date_range) == 1:
            start_date = end_date = date_range[0]
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date = end_date = date_range

    daily_filtered = daily[
        daily["Date"].dt.date.between(start_date, end_date)
    ].copy()

    if not daily_filtered.empty:
        fig = px.line(
            daily_filtered,
            x="Date",
            y="total_units_sold",
            title="Daily Total Units Sold",
            labels={
                "Date": "Date",
                "total_units_sold": "Units Sold",
            },
        )

        st.plotly_chart(fig, use_container_width=True)

        trend_columns = [
            column
            for column in [
                "total_units_sold",
                "total_units_ordered",
                "average_inventory",
                "average_demand_forecast",
                "average_price",
            ]
            if column in daily_filtered.columns
        ]

        st.dataframe(
            daily_filtered[["Date"] + trend_columns],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No daily data exists for the selected dates.")
else:
    st.warning("No valid dates were found in the daily report.")

# --------------------------------------------------
# 8. FORECAST MODEL COMPARISON
# --------------------------------------------------

st.divider()
st.header("Demand Forecasting")

st.markdown(
    "Compare the previous-day baseline with the 7-day moving-average "
    "forecast on the saved test period."
)


def calculate_metrics(frame, actual_column, forecast_column):
    valid = frame[[actual_column, forecast_column]].dropna()

    if valid.empty:
        return None

    errors = valid[actual_column] - valid[forecast_column]

    return {
        "MAE": errors.abs().mean(),
        "RMSE": (errors.pow(2).mean()) ** 0.5,
        "Test Observations": len(valid),
    }


baseline_metrics = calculate_metrics(
    baseline,
    "Units Sold",
    "Baseline Forecast",
)

moving_metrics = calculate_metrics(
    moving,
    "Units Sold",
    "Moving Average Forecast",
)

if baseline_metrics is not None and moving_metrics is not None:
    baseline_mae = baseline_metrics["MAE"]
    moving_mae = moving_metrics["MAE"]
    baseline_rmse = baseline_metrics["RMSE"]
    moving_rmse = moving_metrics["RMSE"]

    improvement = (
        (baseline_mae - moving_mae) / baseline_mae * 100
        if baseline_mae != 0
        else 0
    )

    f1, f2, f3 = st.columns(3)

    f1.metric("Baseline MAE", f"{baseline_mae:,.2f}")
    f2.metric("Moving Average MAE", f"{moving_mae:,.2f}")
    f3.metric(
        "MAE Improvement",
        f"{improvement:.1f}%",
        delta=f"{improvement:.1f}% vs baseline",
    )

    comparison = pd.DataFrame(
        [
            {
                "Model": "Previous-day baseline",
                "MAE": baseline_mae,
                "RMSE": baseline_rmse,
                "Test Observations": baseline_metrics[
                    "Test Observations"
                ],
            },
            {
                "Model": "7-day moving average",
                "MAE": moving_mae,
                "RMSE": moving_rmse,
                "Test Observations": moving_metrics[
                    "Test Observations"
                ],
            },
        ]
    )

    st.subheader("Forecast Accuracy Metrics")
    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True,
    )

    fig = px.bar(
        comparison,
        x="Model",
        y=["MAE", "RMSE"],
        barmode="group",
        title="Forecast Error Comparison (Lower Is Better)",
        labels={"value": "Forecast Error", "Model": "Model"},
    )

    st.plotly_chart(fig, use_container_width=True)

    # Merge on dates to compare actuals and both forecasts.
    baseline_plot = baseline[
        ["Date", "Units Sold", "Baseline Forecast"]
    ].dropna(subset=["Date"])

    moving_plot = moving[
        ["Date", "Moving Average Forecast"]
    ].dropna(subset=["Date"])

    forecast_plot = baseline_plot.merge(
        moving_plot,
        on="Date",
        how="inner",
    ).sort_values("Date")

    if not forecast_plot.empty:
        fig = px.line(
            forecast_plot,
            x="Date",
            y=[
                "Units Sold",
                "Baseline Forecast",
                "Moving Average Forecast",
            ],
            title="Actual vs Forecast Demand",
            labels={
                "Date": "Date",
                "value": "Units Sold",
                "variable": "Series",
            },
        )

        st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Forecast errors are evaluated on the held-out chronological "
        "test period. The moving-average calculation uses prior actual "
        "sales for each test date."
    )
else:
    st.warning(
        "Forecast metrics could not be calculated. Check the forecast "
        "CSV column names and confirm the report files contain data."
    )

# --------------------------------------------------
# 9. INVENTORY RISK MONITORING
# --------------------------------------------------

st.divider()
st.header("Inventory Risk Monitoring")

st.markdown(
    "Prioritize store-product pairs according to estimated stock cover. "
    "The risk thresholds are initial analytical assumptions."
)

risk_statuses = [
    "Critical",
    "Reorder soon",
    "Healthy",
    "Forecast unavailable",
    "Data issue",
]

risk_counts = (
    risk["Risk Status"]
    .value_counts()
    .reindex(risk_statuses, fill_value=0)
)

r1, r2, r3, r4 = st.columns(4)

r1.metric("Critical", f"{int(risk_counts['Critical']):,}")
r2.metric("Reorder Soon", f"{int(risk_counts['Reorder soon']):,}")
r3.metric("Healthy", f"{int(risk_counts['Healthy']):,}")
r4.metric(
    "Forecast Unavailable",
    f"{int(risk_counts['Forecast unavailable']):,}",
)

risk_left, risk_right = st.columns([1, 2])

with risk_left:
    risk_chart_data = (
        risk_counts.rename_axis("Risk Status")
        .reset_index(name="Store-Product Pairs")
    )

    fig = px.pie(
        risk_chart_data,
        names="Risk Status",
        values="Store-Product Pairs",
        title="Inventory Risk Distribution",
        hole=0.45,
    )

    st.plotly_chart(fig, use_container_width=True)

with risk_right:
    st.subheader("Inventory Records")

    selected_risks = st.multiselect(
        "Filter risk statuses",
        options=risk_statuses,
        default=["Critical", "Reorder soon"],
        key="risk_status_filter",
    )

    risk_filtered = risk[
        risk["Risk Status"].isin(selected_risks)
    ].copy()

    available_dimensions = [
        column
        for column in ["Category", "Region"]
        if column in risk_filtered.columns
    ]

    for column in available_dimensions:
        options = sorted(
            risk_filtered[column].dropna().astype(str).unique()
        )

        selected_values = st.multiselect(
            f"Filter by {column.lower()}",
            options=options,
            default=options,
            key=f"risk_{column.lower()}_filter",
        )

        risk_filtered = risk_filtered[
            risk_filtered[column].astype(str).isin(selected_values)
        ]

    if "Stock Cover Days" in risk_filtered.columns:
        risk_filtered = risk_filtered.sort_values(
            "Stock Cover Days",
            na_position="last",
        )

    st.dataframe(
        risk_filtered,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download filtered inventory risk report",
        data=risk_filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_inventory_risk_report.csv",
        mime="text/csv",
    )

# --------------------------------------------------
# 10. PORTFOLIO NOTES
# --------------------------------------------------

st.divider()

with st.expander("About this project and its assumptions"):
    st.markdown(
        """
        **Platform capabilities**
        - Data validation and cleaning
        - SQL-based retail performance reports
        - Daily demand forecasting benchmarks
        - Store-product inventory-risk classification
        - Interactive visual analytics

        **Important limitations**
        - The source retail dataset is synthetic.
        - Inventory risk uses estimated stock cover and simple thresholds.
        - Stock cover is inventory divided by forecast daily demand.
        - Forecast accuracy on historical test data does not guarantee
          future business performance.
        - These outputs are analytical indicators, not live replenishment
          instructions.
        """
    )

st.caption(
    "Supply Chain Intelligence Platform | Retail analytics and demand planning"
)
