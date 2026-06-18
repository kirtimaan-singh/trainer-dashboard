import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Trainer Calendar Dashboard",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Trainer Calendar & Availability Dashboard")

# -----------------------------------
# LOAD DATA WITH ERROR HANDLING
# -----------------------------------
@st.cache_data
def load_data():
    try:
        # Check if file exists
        if not os.path.exists("Enhanced Trainer Activity Log (2).xlsx"):
            st.error("❌ Excel file not found: 'Enhanced Trainer Activity Log (2).xlsx'")
            st.info("Please ensure the file is in the same directory as the app.")
            return None
        
        df = pd.read_excel(
            "Enhanced Trainer Activity Log (2).xlsx",
            engine="openpyxl"
        )

        # Clean column names
        df.columns = df.columns.str.strip()

        # Convert Date column safely
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

        # Clean up missing or broken times by replacing dashes/spaces with None
        df["Start Time"] = df["Start Time"].astype(str).str.strip().replace(['-', 'nan', ''], None)
        df["End Time"] = df["End Time"].astype(str).str.strip().replace(['-', 'nan', ''], None)

        # Create Start and End datetime safely using errors='coerce'
        df["Start"] = pd.to_datetime(
            df["Date"].dt.strftime("%Y-%m-%d") + " " + df["Start Time"],
            errors='coerce'
        )

        df["End"] = pd.to_datetime(
            df["Date"].dt.strftime("%Y-%m-%d") + " " + df["End Time"],
            errors='coerce'
        )

        # Drop rows where dates or times couldn't be parsed
        df = df.dropna(subset=["Date", "Start", "End"])

        return df
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

df = load_data()

if df is None:
    st.stop()

# -----------------------------------
# SIDEBAR FILTERS
# -----------------------------------
st.sidebar.header("🔍 Filters & Settings")

# Date range filter
date_range = st.sidebar.date_input(
    "Date Range",
    value=(df["Date"].min().date(), df["Date"].max().date()),
    min_value=df["Date"].min().date(),
    max_value=df["Date"].max().date()
)

# Capacity/Target Hours Configurator
max_capacity = st.sidebar.slider(
    "Total Capacity Target (Hours)", 
    min_value=40, 
    max_value=300, 
    value=160, 
    step=10,
    help="Set the standard maximum allocated workload hours per trainer for availability analysis."
)

# Trainer filter
trainer_filter = st.sidebar.multiselect(
    "Trainer",
    sorted(df["Trainer Name"].dropna().unique()),
    default=sorted(df["Trainer Name"].dropna().unique())
)

# Activity filter
activity_filter = st.sidebar.multiselect(
    "Activity Type",
    sorted(df["Activity Type"].dropna().unique()),
    default=sorted(df["Activity Type"].dropna().unique())
)

# Apply filters safely
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[
        (df["Trainer Name"].isin(trainer_filter))
        & (df["Activity Type"].isin(activity_filter))
        & (df["Date"].dt.date >= start_date)
        & (df["Date"].dt.date <= end_date)
    ]
else:
    filtered_df = df[
        (df["Trainer Name"].isin(trainer_filter))
        & (df["Activity Type"].isin(activity_filter))
    ]

if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters. Please adjust your criteria.")
    st.stop()

# -----------------------------------
# TOP KPI CARDS
# -----------------------------------
st.subheader("📊 Overall Summary")

col1, col2, col3, col4, col5 = st.columns(5)

total_hours = filtered_df["Duration (Hours)"].sum()
total_activities = len(filtered_df)
unique_trainers = filtered_df["Trainer Name"].nunique()
avg_duration = filtered_df["Duration (Hours)"].mean()
activity_types = filtered_df["Activity Type"].nunique()

col1.metric("📋 Total Activities", total_activities)
col2.metric("👥 Total Trainers", unique_trainers)
col3.metric("⏱️ Total Hours", f"{total_hours:.1f}")
col4.metric("⏲️ Avg Duration", f"{avg_duration:.1f} hrs")
col5.metric("🎯 Activity Types", activity_types)

# -----------------------------------
# TRAINER HOURS & AVAILABILITY DASHBOARD
# -----------------------------------
st.subheader("👨‍🏫 Trainer Workload & Availability Tracker")

trainer_hours = (
    filtered_df.groupby("Trainer Name")["Duration (Hours)"]
    .sum()
    .reset_index()
)
trainer_hours.rename(columns={"Duration (Hours)": "Completed Hours"}, inplace=True)

# Add Capacity and calculate dynamic availability status
trainer_hours["Target Hours"] = max_capacity
trainer_hours["Available Hours"] = trainer_hours["Target Hours"] - trainer_hours["Completed Hours"]

trainer_hours = trainer_hours.sort_values("Completed Hours", ascending=False)

# Dashboard Cards
cols = st.columns(3)

for idx, row in trainer_hours.iterrows():
    with cols[idx % 3]:
        completion = (row["Completed Hours"] / row["Target Hours"]) * 100
        available_display = row["Available Hours"]

        # Color coding metrics based on active availability
        if completion >= 100:
            border_color = "#e74c3c"  # Red (Overbooked / Fully booked)
            status = "🔴 OVERBOOKED / CAPACITY FULL"
            avail_color = "red"
            available_display = 0.0 if row["Available Hours"] < 0 else row["Available Hours"]
        elif completion >= 75:
            border_color = "#f39c12"  # Orange (High utilization)
            status = "⚠️ LIMITED AVAILABILITY"
            avail_color = "#f39c12"
        else:
            border_color = "#2ecc71"  # Green (Plenty of open capacity)
            status = "✅ AVAILABLE FOR SEGMENTS"
            avail_color = "green"

        st.markdown(
            f"""
            <div style="
                background:#ffffff;
                padding:20px;
                border-radius:15px;
                border-left:8px solid {border_color};
                box-shadow:0px 3px 10px rgba(0,0,0,0.1);
                margin-bottom:15px;">
                
                <h3>{row['Trainer Name']}</h3>
                <p style="color:{border_color}; font-weight:bold; font-size:13px; margin-top:-5px;">{status}</p>

                <h4 style="color:green; margin: 5px 0;">
                ✅ Logged Work: {row['Completed Hours']:.1f} hrs
                </h4>

                <h4 style="color:{avail_color}; margin: 5px 0;">
                ⏳ Free Availability: {available_display:.1f} hrs
                </h4>

                <h4 style="color:blue; margin: 5px 0;">
                🎯 Max Target Limit: {row['Target Hours']} hrs
                </h4>

                <div style="
                    background:#f0f0f0;
                    border-radius:10px;
                    overflow:hidden;
                    margin:12px 0 0 0;">
                    <div style="
                        background:{border_color};
                        width:{min(completion, 100):.1f}%;
                        height:20px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        color:white;
                        font-size:12px;
                        font-weight:bold;">
                        {completion:.1f}% Used
                    </div>
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------------------
# VISUAL AVAILABILITY SPLIT CHART
# -----------------------------------
st.subheader("📈 Trainer Allocation vs Availability Matrix")

col1, col2 = st.columns(2)

with col1:
    # Build stacked status visualization chart
    # Ensure chart values display correctly by handling negative availability numbers as fully booked capacity visually
    chart_df = trainer_hours.copy()
    chart_df["Free Space"] = chart_df["Available Hours"].clip(lower=0)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=chart_df["Trainer Name"],
        y=chart_df["Completed Hours"],
        name="Booked Training Hours",
        marker_color="#3498db"
    ))
    fig.add_trace(go.Bar(
        x=chart_df["Trainer Name"],
        y=chart_df["Free Space"],
        name="Remaining Available Slots",
        marker_color="#2ecc71"
    ))

    fig.update_layout(
        barmode="stack",
        height=400,
        xaxis_title="Trainer Name",
        yaxis_title="Total Baseline Hours",
        legend_title="Slot Breakdown"
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# ACTIVITY TYPE BREAKDOWN
# -----------------------------------
with col2:
    activity_breakdown = filtered_df.groupby("Activity Type")["Duration (Hours)"].sum().reset_index()
    activity_breakdown = activity_breakdown.sort_values("Duration (Hours)", ascending=False)
    
    fig_pie = px.pie(
        activity_breakdown,
        values="Duration (Hours)",
        names="Activity Type",
        title="Distribution Profile (Hours by Activity Type)",
        hole=0.4
    )
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------
# ACTIVITY DISTRIBUTION & UTILIZATION
# -----------------------------------
st.subheader("📊 Workload Structures")

col1, col2 = st.columns(2)

with col1:
    trainer_activity_count = filtered_df.groupby(["Trainer Name", "Activity Type"]).size().reset_index(name="Count")
    
    fig_activity = px.bar(
        trainer_activity_count,
        x="Trainer Name",
        y="Count",
        color="Activity Type",
        title="Activity Engagements Density Count",
        barmode="stack"
    )
    fig_activity.update_layout(height=400)
    st.plotly_chart(fig_activity, use_container_width=True)

with col2:
    utilization_data = trainer_hours.copy()
    utilization_data["Utilization %"] = ((utilization_data["Completed Hours"] / utilization_data["Target Hours"]) * 100)
    
    fig_utilization = px.bar(
        utilization_data,
        x="Trainer Name",
        y="Utilization %",
        color="Utilization %",
        color_continuous_scale="RdYlGn_r",  # Reversing color wheel so high utilization alerts visually
        title="Capacity Burn Rate Percentage (%)"
    )
    fig_utilization.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Max Capacity Threshold")
    fig_utilization.update_layout(height=400)
    st.plotly_chart(fig_utilization, use_container_width=True)

# -----------------------------------
# CALENDAR TIMELINE
# -----------------------------------
st.subheader("📅 Trainer Schedule Distribution Timeline")

if len(filtered_df) > 0:
    calendar_fig = px.timeline(
        filtered_df,
        x_start="Start",
        x_end="End",
        y="Trainer Name",
        color="Activity Type",
        hover_data=["Activity Type", "Duration (Hours)"]
    )
    calendar_fig.update_yaxes(autorange="reversed")
    calendar_fig.update_layout(
        height=500,
        xaxis_title="Timeline Calendar Stream",
        yaxis_title="Active Personnel"
    )
    st.plotly_chart(calendar_fig, use_container_width=True)
else:
    st.warning("No operational tracks logged within range.")

# -----------------------------------
# TREND ANALYSIS
# -----------------------------------
st.subheader("📈 Activity Trend Over Time")

daily_hours = filtered_df.groupby(filtered_df["Date"].dt.date)["Duration (Hours)"].sum().reset_index()
daily_hours.columns = ["Date", "Hours"]
daily_hours = daily_hours.sort_values("Date")

fig_trend = px.line(
    daily_hours,
    x="Date",
    y="Hours",
    title="Daily Training Volume Curves",
    markers=True
)
fig_trend.update_layout(height=400)
st.plotly_chart(fig_trend, use_container_width=True)

# -----------------------------------
# DETAILED DATA TABLE
# -----------------------------------
st.subheader("📋 Registry Log Records")

search_term = st.text_input("🔍 Search entries contextually (by Activity Type or Trainer Name):")

if search_term:
    display_df = filtered_df[
        (filtered_df["Activity Type"].str.contains(search_term, case=False, na=False)) |
        (filtered_df["Trainer Name"].str.contains(search_term, case=False, na=False))
    ]
else:
    display_df = filtered_df

st.dataframe(display_df, use_container_width=True, height=400)
st.write(f"Displaying {len(display_df)} of {len(filtered_df)} items indexed.")

# -----------------------------------
# STATISTICS SECTION
# -----------------------------------
st.subheader("📊 Structural Aggregates")
# -----------------------------------
# STATISTICS SECTION
# -----------------------------------
st.subheader("📊 Structural Aggregates")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Highest Bound Workload Resource",
        trainer_hours.iloc[0]["Trainer Name"] if not trainer_hours.empty else "N/A",
        f"{trainer_hours.iloc[0]['Completed Hours']:.1f} Total Hrs Logged" if not trainer_hours.empty else "0 hrs"
    )

with col2:
    if len(filtered_df) > 0:
        most_common_act = filtered_df["Activity Type"].mode()[0]
        act_count = len(filtered_df[filtered_df["Activity Type"] == most_common_act])
        metric_label = f"{act_count} Logged Cycles"
    else:
        most_common_act = "N/A"
        metric_label = "0 instances"

    st.metric(
        "Dominant System Function",
        most_common_act,
        metric_label
    )

with col3:
    st.metric(
        "Active Operation Window Range",
        f"{filtered_df['Date'].min().date()} — {filtered_df['Date'].max().date()}" if len(filtered_df) > 0 else "N/A",
        f"{(filtered_df['Date'].max() - filtered_df['Date'].min()).days + 1} Spanning Days" if len(filtered_df) > 0 else "0 days"
    )
