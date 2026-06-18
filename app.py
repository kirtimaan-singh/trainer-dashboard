import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Trainer Command Center",
    page_icon="📅",
    layout="wide"
)

# Custom header styling
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .subtitle { font-size: 16px; color: #4B5563; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📅 Trainer Command Center</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Quickly track trainer engagement schedules, workload capacities, and real-time availability.</div>', unsafe_allow_html=True)

# -----------------------------------
# LOAD DATA WITH ERROR HANDLING
# -----------------------------------
@st.cache_data
def load_data():
    try:
        if not os.path.exists("Enhanced Trainer Activity Log (2).xlsx"):
            st.error("❌ Excel file not found: 'Enhanced Trainer Activity Log (2).xlsx'")
            return None
        
        df = pd.read_excel("Enhanced Trainer Activity Log (2).xlsx", engine="openpyxl")
        df.columns = df.columns.str.strip()
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

        df["Start Time"] = df["Start Time"].astype(str).str.strip().replace(['-', 'nan', ''], None)
        df["End Time"] = df["End Time"].astype(str).str.strip().replace(['-', 'nan', ''], None)

        df["Start"] = pd.to_datetime(df["Date"].dt.strftime("%Y-%m-%d") + " " + df["Start Time"], errors='coerce')
        df["End"] = pd.to_datetime(df["Date"].dt.strftime("%Y-%m-%d") + " " + df["End Time"], errors='coerce')

        df = df.dropna(subset=["Date", "Start", "End"])
        return df
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

df = load_data()
if df is None:
    st.stop()

# -----------------------------------
# SIDEBAR CONTROLS
# -----------------------------------
st.sidebar.header("⚙️ Global Setup")

date_range = st.sidebar.date_input(
    "Date Window Range",
    value=(df["Date"].min().date(), df["Date"].max().date()),
    min_value=df["Date"].min().date(),
    max_value=df["Date"].max().date()
)

max_capacity = st.sidebar.slider(
    "Baseline Capacity Target (Hours)", 
    min_value=10, max_value=300, value=160, step=10
)

# Apply global baseline datetime filtering first
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    base_filtered_df = df[(df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)]
else:
    base_filtered_df = df.copy()

# -----------------------------------
# 1-CLICK INTERACTIVE DRILL DOWN SELECTION
# -----------------------------------
st.markdown("### 🎯 Single-Click View Mode")
trainer_options = ["✨ View All Trainers Combined"] + sorted(base_filtered_df["Trainer Name"].dropna().unique().tolist())
selected_mode = st.selectbox("Choose view context:", trainer_options)

# Isolate dataset based on selector choices 
if selected_mode == "✨ View All Trainers Combined":
    filtered_df = base_filtered_df.copy()
    is_single_trainer = False
else:
    filtered_df = base_filtered_df[base_filtered_df["Trainer Name"] == selected_mode]
    is_single_trainer = True

if filtered_df.empty:
    st.warning("⚠️ No scheduled records logged inside this criteria combo.")
    st.stop()

# -----------------------------------
# SUMMARY OVERVIEW
# -----------------------------------
st.markdown("---")
total_hours = filtered_df["Duration (Hours)"].sum()
total_activities = len(filtered_df)
unique_trainers = filtered_df["Trainer Name"].nunique()
avg_duration = filtered_df["Duration (Hours)"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📋 Total Scheduled Sessions", total_activities)
col2.metric("👥 Active Instructors", unique_trainers if not is_single_trainer else "Focused View")
col3.metric("⏱️ Cumulative Logged Hours", f"{total_hours:.1f} Hrs")
col4.metric("⏲️ Mean Session Length", f"{avg_duration:.1f} Hrs")

# -----------------------------------
# WORKLOAD CAPACITY CARDS
# -----------------------------------
st.markdown("### 👨‍🏫 Capacity Burn & Allocation Metrics")

trainer_hours = filtered_df.groupby("Trainer Name")["Duration (Hours)"].sum().reset_index()
trainer_hours.rename(columns={"Duration (Hours)": "Completed Hours"}, inplace=True)
trainer_hours["Target Hours"] = max_capacity
trainer_hours["Available Hours"] = trainer_hours["Target Hours"] - trainer_hours["Completed Hours"]
trainer_hours = trainer_hours.sort_values("Completed Hours", ascending=False)

# Render metric layout cards dynamically
card_cols = st.columns(min(3, len(trainer_hours)))
for idx, row in trainer_hours.iterrows():
    completion_pct = (row["Completed Hours"] / row["Target Hours"]) * 100
    free_hours = row["Available Hours"]
    
    if completion_pct >= 100:
        color, status_lbl = "#EF4444", "🔴 OVERBOOKED / CAPACITY MAXED"
        free_hours = max(0, free_hours)
    elif completion_pct >= 75:
        color, status_lbl = "#F59E0B", "⚠️ LIMITED OPEN RUNTIME"
    else:
        color, status_lbl = "#10B981", "✅ FLEXIBLE FOR ASSIGNMENTS"

    with card_cols[idx % min(3, len(trainer_hours))]:
        st.markdown(f"""
            <div style="background:#F9FAFB; padding:18px; border-radius:12px; border-left:6px solid {color}; box-shadow:0 1px 3px rgba(0,0,0,0.05); margin-bottom:12px;">
                <h4 style="margin:0 0 4px 0; color:#111827;">{row['Trainer Name']}</h4>
                <p style="color:{color}; font-size:12px; font-weight:bold; margin:0 0 12px 0;">{status_lbl}</p>
                <div style="font-size:13px; color:#374151; line-height: 1.6;">
                    <b>Logged Work:</b> {row['Completed Hours']:.1f} hrs<br>
                    <b>Open Capacity:</b> {free_hours:.1f} hrs<br>
                    <b>Target Baseline:</b> {row['Target Hours']} hrs
                </div>
                <div style="background:#E5E7EB; border-radius:4px; overflow:hidden; margin-top:12px; height:8px;">
                    <div style="background:{color}; width:{min(completion_pct, 100):.1f}%; height:100%;"></div>
                </div>
                <div style="text-align:right; font-size:11px; color:#6B7280; font-weight:bold; margin-top:4px;">{completion_pct:.1f}% Capacity Utilized</div>
            </div>
        """, unsafe_allow_html=True)

# -----------------------------------
# VISUAL MATRICES & CHARTS
# -----------------------------------
st.markdown("### 📊 Operational Visualizations")
layout_col1, layout_col2 = st.columns(2)

with layout_col1:
    # Stacked chart layout logic
    chart_data = trainer_hours.copy()
    chart_data["Free Availability"] = chart_data["Available Hours"].clip(lower=0)
    
    fig_matrix = go.Figure()
    fig_matrix.add_trace(go.Bar(x=chart_data["Trainer Name"], y=chart_data["Completed Hours"], name="Booked Hours", marker_color="#3B82F6"))
    fig_matrix.add_trace(go.Bar(x=chart_data["Trainer Name"], y=chart_data["Free Availability"], name="Remaining Availability", marker_color="#10B981"))
    fig_matrix.update_layout(barmode="stack", height=350, margin=dict(l=20, r=20, t=30, b=20), xaxis_title="Instructor Profile", yaxis_title="Hours Breakdown")
    st.plotly_chart(fig_matrix, use_container_width=True)

with layout_col2:
    activity_profile = filtered_df.groupby("Activity Type")["Duration (Hours)"].sum().reset_index()
    fig_pie = px.pie(activity_profile, values="Duration (Hours)", names="Activity Type", title="Logged Profile Breakdown by Type", hole=0.4)
    fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------
# CALENDAR TIMELINE VIEW
# -----------------------------------
st.markdown("### 📅 Program Distribution Timeline")
fig_timeline = px.timeline(
    filtered_df, 
    x_start="Start", x_end="End", 
    y="Trainer Name" if not is_single_trainer else "Activity Type", 
    color="Activity Type",
    hover_data=["Subject", "Duration (Hours)"]
)
fig_timeline.update_yaxes(autorange="reversed")
fig_timeline.update_layout(height=300, margin=dict(l=20, r=20, t=10, b=20), xaxis_title="Daily Time Coordinates", yaxis_title="")
st.plotly_chart(fig_timeline, use_container_width=True)

# -----------------------------------
# SEARCHABLE DATA REGISTRY
# -----------------------------------
st.markdown("### 📋 Interactive Activity Registry")
search_term = st.text_input("🔍 Filter matching row entries instantly (type any Subject, University, or Activity):")

if search_term:
    display_df = filtered_df[
        filtered_df["Activity Type"].str.contains(search_term, case=False, na=False) |
        filtered_df["Trainer Name"].str.contains(search_term, case=False, na=False) |
        filtered_df.astype(str).apply(lambda row: row.str.contains(search_term, case=False).any(), axis=1)
    ]
else:
    display_df = filtered_df

st.dataframe(display_df[["Date", "Trainer Name", "Subject", "Activity Type", "Duration (Hours)", "Start Time", "End Time"]], use_container_width=True, height=250)
st.caption(f"Showing {len(display_df)} of {len(filtered_df)} total matching database rows.")
