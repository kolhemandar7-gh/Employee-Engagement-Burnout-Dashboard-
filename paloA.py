import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Employee Engagement & Burnout Dashboard",
    page_icon="🧠",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("Palo Alto Networks.csv")

df = load_data()

# -------------------- HEADER WITH LOGO --------------------
col_logo, col_title = st.columns([1, 5])

with col_logo:
    st.image(
        "palo logo.png",
        width=150
    )

with col_title:
    st.title("Employee Engagement & Burnout Analytics Dashboard")
    st.markdown(
        "**Employee Engagement, Satisfaction, and Burnout Diagnostic Analysis**"
    )
    
# ---------------- DATA PREP ----------------
df["AttritionFlag"] = df["Attrition"].map({"Yes": 1, "No": 0})
df["OverTimeFlag"] = df["OverTime"].map({"Yes": 1, "No": 0})

# Engagement Health Index (Unified Score)
df["EngagementIndex"] = (
    df["JobSatisfaction"] +
    df["EnvironmentSatisfaction"] +
    df["WorkLifeBalance"]
) / 3

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔍 Filters")

dept = st.sidebar.multiselect(
    "Select Department",
    options=df["Department"].unique(),
    default=df["Department"].unique()
)

df = df[df["Department"].isin(dept)]

# ---------------- KPI SECTION ----------------

total_employees = len(df)
attrition_count = df[df["Attrition"] == 1].shape[0]
attrition_rate = (attrition_count / total_employees) * 100 if total_employees > 0 else 0


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "📊 Avg Engagement Index",
    round(df["EngagementIndex"].mean(), 2)
)

col2.metric(
    "⏱️ Overtime %",
    f"{round(df['OverTimeFlag'].mean()*100, 1)}%"
)

col3.metric(
    label="📉 Attrition Rate",
    value=f"{attrition_rate:.2f}%"
)

col4.metric(
    "🔥 High Burnout Risk %",
    f"{round(len(df[(df['OverTimeFlag']==1) & (df['WorkLifeBalance']<=2)]) / len(df) * 100, 1)}%"
)

st.markdown("---")

# ---------------- ENGAGEMENT HEALTH INDEX ----------------
st.subheader("📌 Unified Engagement Health Index")

engagement_counts = (
    df["EngagementIndex"]
    .value_counts()
    .reset_index()
)

engagement_counts.columns = ["EngagementIndex", "Count"]
engagement_counts = engagement_counts.sort_values("EngagementIndex")
fig_engagement = px.bar(
    engagement_counts,
    x="EngagementIndex",
    y="Count",
    title="Distribution of Engagement Health Index",
    color_discrete_sequence=["#2E86C1"]
)

st.plotly_chart(fig_engagement, use_container_width=True)

# ---------------- BURNOUT PRONE GROUPS ----------------
st.subheader("🔥 Burnout-Prone Employee Groups")

# Group Data
burnout_df = df.groupby("JobRole").agg({
    "OverTimeFlag": "mean",
    "EngagementIndex": "mean",
    "AttritionFlag": "mean"
}).reset_index()

# Sort by Overtime (Higher = More Burnout Risk)
burnout_df = burnout_df.sort_values(by="OverTimeFlag", ascending=True)

# ---- Chart 1: Overtime (Burnout Signal) ----
fig_overtime = px.bar(
    burnout_df,
    x="OverTimeFlag",
    y="JobRole",
    orientation="h",
    title="Average Overtime by Job Role",
    text="OverTimeFlag",
)

fig_overtime.update_layout(
    template="plotly_white",
    height=500,
    title_x=0.3
)

fig_overtime.update_traces(texttemplate="%{text:.2f}", textposition="outside")

st.plotly_chart(fig_overtime, use_container_width=True)


# ---- Chart 2: Engagement ----
fig_engagement = px.bar(
    burnout_df,
    x="EngagementIndex",
    y="JobRole",
    orientation="h",
    title="Average Engagement Score by Job Role",
    text="EngagementIndex",
)

fig_engagement.update_layout(
    template="plotly_white",
    height=500,
    title_x=0.3
)

fig_engagement.update_traces(texttemplate="%{text:.2f}", textposition="outside")

st.plotly_chart(fig_engagement, use_container_width=True)





# ---------------- INTERACTION ANALYSIS ----------------
st.subheader("⚖️ Overtime vs Work-Life Balance vs Satisfaction")

fig_interaction = px.box(
    df,
    x="OverTime",
    y="WorkLifeBalance",
    color="OverTime",
    title="Impact of Overtime on Work-Life Balance"
)
st.plotly_chart(fig_interaction, use_container_width=True)

fig_satisfaction = px.line(
    df.groupby("WorkLifeBalance", as_index=False)
      .agg({"JobSatisfaction": "mean"}),
    x="WorkLifeBalance",
    y="JobSatisfaction",
    markers=True,
    title="Work-Life Balance vs Job Satisfaction"
)

st.plotly_chart(fig_satisfaction, use_container_width=True)


# ---------------- PREVENTIVE INSIGHTS ----------------
st.subheader("🚨 Preventive Burnout Risk Insights")

risk_df = df[
    (df["OverTimeFlag"] == 1) &
    (df["WorkLifeBalance"] <= 2) &
    (df["EngagementIndex"] <= 2.5)
]

st.warning(
    f"⚠️ {len(risk_df)} employees identified as HIGH burnout risk "
    f"({round(len(risk_df)/len(df)*100, 1)}% of workforce)"
)

st.dataframe(
    risk_df[[
        "Department",
        "JobRole",
        "WorkLifeBalance",
        "JobSatisfaction",
        "EngagementIndex"
    ]].head(10)
)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("📊 Designed for proactive employee experience & burnout prevention")
