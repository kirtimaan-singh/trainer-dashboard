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

st.title("📅 Trainer Calendar Dashboard")

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

        # Clean up missing or broken times by replacing dashes/spaces with NaN
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
        return df
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

df = load_data()
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
    # Fallback if the user is in the middle of picking a date range
    filtered_df = df[
        (df["Trainer Name"].isin(trainer_filter))
        & (df["Activity Type"].isin(activity_filter))
    ]

# Activity filter
activity_filter = st.sidebar.multiselect(
    "Activity Type",
    sorted(df["Activity Type"].dropna().unique()),
    default=sorted(df["Activity Type"].dropna().unique())
)

# Apply filters
filtered_df = df[
    (df["Trainer Name"].isin(trainer_filter))
    & (df["Activity Type"].isin(activity_filter))
    & (df["Date"].dt.date >= date_range[0])
    & (df["Date"].dt.date <= date_range[1])
]

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
# TRAINER HOURS DASHBOARD
# -----------------------------------
st.subheader("👨‍🏫 Trainer Hours Progress Dashboard")

TARGET_HOURS = 160

trainer_hours = (
    filtered_df.groupby("Trainer Name")["Duration (Hours)"]
    .sum()
    .reset_index()
)

trainer_hours.rename(
    columns={"Duration (Hours)": "Completed Hours"},
    inplace=True
)

trainer_hours["Target Hours"] = TARGET_HOURS

trainer_hours["Remaining Hours"] = (
    trainer_hours["Target Hours"]
    - trainer_hours["Completed Hours"]
)

trainer_hours["Remaining Hours"] = trainer_hours[
    "Remaining Hours"
].clip(lower=0)

trainer_hours = trainer_hours.sort_values("Completed Hours", ascending=False)

# Dashboard Cards
cols = st.columns(3)

for idx, row in trainer_hours.iterrows():
    with cols[idx % 3]:
        completion = (
            row["Completed Hours"] /
            row["Target Hours"]
        ) * 100

        # Color code based on completion
        if completion >= 100:
            border_color = "#2ecc71"  # Green
            status = "✅ COMPLETED"
        elif completion >= 75:
            border_color = "#f39c12"  # Orange
            status = "⚠️ ON TRACK"
        else:
            border_color = "#e74c3c"  # Red
            status = "🔴 BEHIND"

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
                <p style="color:{border_color}; font-weight:bold; font-size:14px;">{status}</p>

                <h4 style="color:green;">
                ✅ Completed: {row['Completed Hours']:.1f} hrs
                </h4>

                <h4 style="color:red;">
                ⏳ Remaining: {row['Remaining Hours']:.1f} hrs
                </h4>

                <h4 style="color:blue;">
                🎯 Target: {row['Target Hours']} hrs
                </h4>

                <div style="
                    background:#f0f0f0;
                    border-radius:10px;
                    overflow:hidden;
                    margin:10px 0;">
                    <div style="
                        background:{border_color};
                        width:{completion}%;
                        height:20px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        color:white;
                        font-size:12px;
                        font-weight:bold;">
                        {completion:.1f}%
                    </div>
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------------------
# HOURS CHART
# -----------------------------------
st.subheader("📈 Trainer Hours Comparison")

col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=trainer_hours["Trainer Name"],
            y=trainer_hours["Completed Hours"],
            name="Completed Hours",
            marker_color="green"
        )
    )

    fig.add_trace(
        go.Bar(
            x=trainer_hours["Trainer Name"],
            y=trainer_hours["Remaining Hours"],
            name="Remaining Hours",
            marker_color="red"
        )
    )

    fig.update_layout(
        barmode="stack",
        height=400,
        xaxis_title="Trainer",
        yaxis_title="Hours",
        legend_title="Hours Status"
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
        title="Hours by Activity Type",
        hole=0.4
    )
    
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------
# ACTIVITY DISTRIBUTION
# -----------------------------------
st.subheader("📊 Activity Distribution by Trainer")

col1, col2 = st.columns(2)

with col1:
    trainer_activity_count = filtered_df.groupby(["Trainer Name", "Activity Type"]).size().reset_index(name="Count")
    
    fig_activity = px.bar(
        trainer_activity_count,
        x="Trainer Name",
        y="Count",
        color="Activity Type",
        title="Activity Count by Trainer & Type",
        barmode="stack"
    )
    
    fig_activity.update_layout(height=400)
    st.plotly_chart(fig_activity, use_container_width=True)

with col2:
    # Utilization Rate
    utilization_data = trainer_hours.copy()
    utilization_data["Utilization %"] = (
        (utilization_data["Completed Hours"] / utilization_data["Target Hours"]) * 100
    ).clip(upper=100)
    
    fig_utilization = px.bar(
        utilization_data,
        x="Trainer Name",
        y="Utilization %",
        color="Utilization %",
        color_continuous_scale="RdYlGn",
        title="Trainer Utilization Rate",
        range_color=[0, 100]
    )
    
    fig_utilization.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Target")
    fig_utilization.update_layout(height=400)
    st.plotly_chart(fig_utilization, use_container_width=True)

# -----------------------------------
# CALENDAR TIMELINE
# -----------------------------------
st.subheader("📅 Trainer Activity Timeline")

if len(filtered_df) > 0:
    calendar_fig = px.timeline(
        filtered_df,
        x_start="Start",
        x_end="End",
        y="Trainer Name",
        color="Activity Type",
        hover_data=[
            "Activity Type",
            "Duration (Hours)"
        ]
    )

    calendar_fig.update_yaxes(autorange="reversed")

    calendar_fig.update_layout(
        height=500,
        xaxis_title="Time",
        yaxis_title="Trainer"
    )

    st.plotly_chart(calendar_fig, use_container_width=True)
else:
    st.warning("No data available for the selected filters.")

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
    title="Daily Training Hours Trend",
    markers=True
)

fig_trend.update_layout(height=400)
st.plotly_chart(fig_trend, use_container_width=True)

# -----------------------------------
# DETAILED DATA TABLE
# -----------------------------------
st.subheader("📋 Activity Details")

# Add search functionality
search_term = st.text_input("🔍 Search activities (by activity type or trainer):")

if search_term:
    display_df = filtered_df[
        (filtered_df["Activity Type"].str.contains(search_term, case=False, na=False)) |
        (filtered_df["Trainer Name"].str.contains(search_term, case=False, na=False))
    ]
else:
    display_df = filtered_df

st.dataframe(
    display_df,
    use_container_width=True,
    height=400
)

st.write(f"Showing {len(display_df)} of {len(filtered_df)} activities")

# -----------------------------------
# STATISTICS SECTION
# -----------------------------------
st.subheader("📊 Detailed Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Most Active Trainer",
        trainer_hours.iloc[0]["Trainer Name"],
        f"{trainer_hours.iloc[0]['Completed Hours']:.1f} hrs"
    )

with col2:
    st.metric(
        "Most Common Activity",
        filtered_df["Activity Type"].mode()[0] if len(filtered_df) > 0 else "N/A",
        f"{len(filtered_df[filtered_df['Activity Type'] == filtered_df['Activity Type'].mode()[0]])} times"
    )

with col3:
    st.metric(
        "Date Range",
        f"{filtered_df['Date'].min().date()} to {filtered_df['Date'].max().date()}",
        f"{(filtered_df['Date'].max() - filtered_df['Date'].min()).days + 1} days"
    )

# -----------------------------------
# EXPORT OPTIONS
# -----------------------------------
st.subheader("📥 Export Options")

col1, col2, col3 = st.columns(3)

with col1:
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv,
        file_name=f"trainer_activity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

with col2:
    # Excel export
    from io import BytesIO
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, sheet_name='Activities', index=False)
        trainer_hours.to_excel(writer, sheet_name='Summary', index=False)
    
    buffer.seek(0)
    
    st.download_button(
        label="📊 Download Excel Report",
        data=buffer,
        file_name=f"trainer_activity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col3:
    st.info("✅ Data exports include filtered data and summary sheets")

# -----------------------------------
# FOOTER
# -----------------------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#888; font-size:12px;">
        <p>Trainer Calendar Dashboard | Last Updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
    </div>
    """,
    unsafe_allow_html=True
)
