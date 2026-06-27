import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Thales Group - 6G Smart Factory Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONSTANTS & STYLING ---
CYAN = "#00d4ff"
GREEN = "#00c878"
AMBER = "#f5a623"
RED = "#ff4d6d"
PURPLE = "#8b5cf6"
NAVY = "#050d1a"
CARD = "#071832"
BORDER = "#1a3a5c"

EFF_COLOR = {"High": GREEN, "Medium": AMBER, "Low": RED}
MODE_COLOR = {"Active": CYAN, "Idle": PURPLE, "Maintenance": AMBER}

# Custom CSS to match the Thales Dashboard UI
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {NAVY};
        color: #e0f0ff;
    }}
    [data-tested="stHeader"] {{
        background-color: rgba(7, 16, 34, 0.95);
        border-bottom: 1px solid {BORDER};
    }}
    .kpi-card {{
        background: linear-gradient(135deg, {CARD}, #0a2040);
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }}
    .section-title {{
        border-left: 3px solid {CYAN};
        padding-left: 10px;
        margin: 18px 0 12px;
        font-size: 14px;
        font-weight: 700;
        color: #e0f0ff;
        letter-spacing: 1px;
        text-transform: uppercase;
    }}
    .insight-box {{
        background: rgba(0, 212, 255, 0.06);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-left: 3px solid {CYAN};
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 13px;
        color: rgba(200, 230, 255, 0.85);
        line-height: 1.6;
        margin-top: 10px;
    }}
    .recommendation-box {{
        background: rgba(0, 200, 120, 0.06);
        border: 1px solid rgba(0, 200, 120, 0.2);
        border-left: 3px solid {GREEN};
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 12px;
        color: rgba(200, 240, 220, 0.85);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- DATA PREPARATION ---

EFF_DIST = pd.DataFrame([
    {"name": "High", "value": 2986, "pct": 3.0},
    {"name": "Medium", "value": 19189, "pct": 19.2},
    {"name": "Low", "value": 77825, "pct": 77.8},
])

MODE_DIST = pd.DataFrame([
    {"mode": "Active", "count": 70054, "High": 2124, "Medium": 13496, "Low": 54434},
    {"mode": "Idle", "count": 20057, "High": 570, "Medium": 3792, "Low": 15695},
    {"mode": "Maintenance", "count": 9889, "High": 292, "Medium": 1901, "Low": 7696},
])

EFF_METRICS = pd.DataFrame([
    {"status": "High", "error": 1.01, "speed": 450.8, "latency": 25.3, "packetLoss": 2.53, "defect": 4.93,
     "nsi": 0.494},
    {"status": "Medium", "error": 2.73, "speed": 334.1, "latency": 25.6, "packetLoss": 2.49, "defect": 4.99,
     "nsi": 0.496},
    {"status": "Low", "error": 8.93, "speed": 254.9, "latency": 25.6, "packetLoss": 2.49, "defect": 5.02, "nsi": 0.495},
])

LATENCY_BAND = pd.DataFrame([
    {"band": "0–15 ms", "High %": 3.0, "Medium %": 19.1, "Low %": 77.9, "speed": 275.8, "error": 7.50},
    {"band": "15–30 ms", "High %": 3.1, "Medium %": 19.1, "Low %": 77.8, "speed": 275.9, "error": 7.51},
    {"band": "30–45 ms", "High %": 2.9, "Medium %": 19.3, "Low %": 77.8, "speed": 276.5, "error": 7.50},
    {"band": "45–50 ms", "High %": 2.9, "Medium %": 19.2, "Low %": 77.8, "speed": 274.6, "error": 7.51},
])

PL_BAND = pd.DataFrame([
    {"band": "<1%", "Low %": 77.8, "error": 7.51, "defect": 5.00},
    {"band": "1–2%", "Low %": 77.8, "error": 7.50, "defect": 5.01},
    {"band": "2–3%", "Low %": 77.8, "error": 7.54, "defect": 5.00},
    {"band": ">3%", "Low %": 77.9, "error": 7.48, "defect": 5.02},
])

CORR_DATA = pd.DataFrame([
    {"feature": "Error Rate", "corr": -0.604},
    {"feature": "Prod Speed", "corr": 0.334},
    {"feature": "Temperature", "corr": 0.004},
    {"feature": "Power", "corr": 0.001},
    {"feature": "Packet Loss", "corr": 0.001},
    {"feature": "Latency", "corr": -0.002},
    {"feature": "Vibration", "corr": 0.000},
    {"feature": "Maintenance", "corr": -0.003},
    {"feature": "Defect Rate", "corr": -0.006},
]).sort_values("corr")

# Generate Scatter Data
np.random.seed(42)
scatter_list = []
for i in range(120):
    eff = "High" if i < 10 else "Medium" if i < 35 else "Low"
    err_base = 1 if eff == "High" else 2.7 if eff == "Medium" else 8.9
    spd_base = 450 if eff == "High" else 334 if eff == "Medium" else 255
    scatter_list.append({
        "error": max(0.0, err_base + (np.random.rand() - 0.5) * 2),
        "speed": max(50.0, spd_base + (np.random.rand() - 0.5) * 60),
        "latency": 1 + np.random.rand() * 49,
        "eff": eff
    })
SCATTER_DATA = pd.DataFrame(scatter_list)

RADAR_DATA = pd.DataFrame([
    {"metric": "Error Control", "High": 95, "Medium": 65, "Low": 20},
    {"metric": "Prod Speed", "High": 92, "Medium": 67, "Low": 51},
    {"metric": "Network Latency", "High": 51, "Medium": 49, "Low": 49},
    {"metric": "Packet Loss", "High": 50, "Medium": 50, "Low": 49},
    {"metric": "Defect Rate", "High": 52, "Medium": 51, "Low": 50},
    {"metric": "NSI", "High": 49, "Medium": 50, "Low": 50},
])

HOURLY_TREND = pd.DataFrame([
    {
        "hour": f"{h}:00",
        "Active": 2400 + np.sin(h / 3.8) * 1800 + np.random.rand() * 300,
        "Idle": 600 + np.random.rand() * 200,
        "Maintenance": 300 + np.random.rand() * 100,
    } for h in range(24)
])


# --- UI COMPONENTS ---

def kpi_card(label, value, sub, accent=False, warn=False):
    color = CYAN if accent else RED if warn else "#e0f0ff"
    border_color = CYAN if accent else RED if warn else BORDER
    st.markdown(f"""
        <div class="kpi-card" style="border-color: {border_color};">
            <div style="font-size:11px; color:rgba(150,190,240,0.6); letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;">{label}</div>
            <div style="font-size:24px; font-weight:800; color:{color}; line-height:1; margin-bottom:4px;">{value}</div>
            <div style="font-size:11px; color:rgba(150,190,240,0.45);">{sub}</div>
        </div>
    """, unsafe_allow_html=True)


def section_title(text):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def insight_box(text, color=CYAN):
    st.markdown(f'<div class="insight-box" style="border-left-color: {color};">{text}</div>', unsafe_allow_html=True)


def recommendation_box(title, text):
    st.markdown(f"""
        <div class="recommendation-box">
            <strong style="color:{GREEN};">{title}</strong><br/>{text}
        </div>
    """, unsafe_allow_html=True)


# --- HEADER ---
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"""
        <div style="font-size:24px; font-weight:900; letter-spacing:2px; background:linear-gradient(90deg,{CYAN},#0077b6); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            ⚡ THALES GROUP — 6G SMART FACTORY ANALYTICS
        </div>
        <div style="font-size:10px; color:rgba(150,190,255,0.45); letter-spacing:3px; text-transform:uppercase; margin-top:2px;">
            Impact of 6G Network Performance on Manufacturing Efficiency · FY 2025
        </div>
    """, unsafe_allow_html=True)

with col2:
    eff_filter = st.multiselect("Efficiency Filter", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])

# --- TABS ---
tab_id = st.tabs(
    ["📊 Overview", "🌐 Network Performance", "⚙️ Efficiency Analysis", "🔬 Quality & Error Impact", "💡 6G Optimization"])

# --- TAB 1: OVERVIEW ---
with tab_id[0]:
    kpi_cols = st.columns(6)
    with kpi_cols[0]: kpi_card("Total Records", "100,000", "FY 2025 dataset", accent=True)
    with kpi_cols[1]: kpi_card("High Efficiency", "3.0%", "of all records", warn=True)
    with kpi_cols[2]: kpi_card("Avg Latency", "25.6 ms", "6G network")
    with kpi_cols[3]: kpi_card("Avg Packet Loss", "2.49%", "data integrity")
    with kpi_cols[4]: kpi_card("Avg Error Rate", "7.50%", "operational")
    with kpi_cols[5]: kpi_card("Avg Speed", "274.9", "units / hr")

    chart_cols = st.columns(3)

    with chart_cols[0]:
        section_title("Efficiency Status Distribution")
        fig = px.pie(EFF_DIST, values='value', names='name', hole=0.6,
                     color='name', color_discrete_map=EFF_COLOR)
        fig.update_layout(showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font_color="#c0d8f0", margin=dict(t=0, b=0, l=0, r=0), height=250)
        st.plotly_chart(fig, use_container_width=True)

    with chart_cols[1]:
        section_title("Operation Mode Split")
        fig = px.bar(MODE_DIST, x='mode', y='count', color='mode', color_discrete_map=MODE_COLOR)
        fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font_color="#c0d8f0", height=250, margin=dict(t=20, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    with chart_cols[2]:
        section_title("Efficiency by Operation Mode")
        fig = px.bar(MODE_DIST, x='mode', y=['High', 'Medium', 'Low'],
                     color_discrete_map=EFF_COLOR, barmode='stack')
        fig.update_layout(legend_title="", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font_color="#c0d8f0", height=250, margin=dict(t=20, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    section_title("Key Metrics by Efficiency Class")
    st.dataframe(EFF_METRICS, use_container_width=True, hide_index=True)

# --- TAB 2: NETWORK PERFORMANCE ---
with tab_id[1]:
    kpi_cols = st.columns(4)
    with kpi_cols[0]: kpi_card("Min Latency", "1.0 ms", "Best observed")
    with kpi_cols[1]: kpi_card("Max Latency", "50.0 ms", "Worst observed")
    with kpi_cols[2]: kpi_card("Min Packet Loss", "0.00%", "Best observed")
    with kpi_cols[3]: kpi_card("Max Packet Loss", "5.00%", "Worst observed")

    col_a, col_b = st.columns(2)
    with col_a:
        section_title("Network Latency Distribution by Efficiency")
        fig = px.bar(LATENCY_BAND, x='band', y=['High %', 'Medium %', 'Low %'],
                     color_discrete_map=EFF_COLOR, barmode='group')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#c0d8f0", height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        section_title("Packet Loss Band → Low Efficiency % & Error Rate")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=PL_BAND['band'],
            y=PL_BAND['Low %'],
            name="Low Eff %",
            marker=dict(color=RED)
        ), secondary_y=False)
        fig.add_trace(
            go.Scatter(
                x=PL_BAND['band'],
                y=PL_BAND['error'],
                name="Error Rate",
                line=dict(color=AMBER, width=3)
            ),
            secondary_y=True
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="#c0d8f0",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)


    col_c, col_d = st.columns(2)
    with col_c:
        section_title("Latency vs Packet Loss — Network Quality Map")
        fig = px.scatter(SCATTER_DATA, x='latency', y='error', color='eff', color_discrete_map=EFF_COLOR, opacity=0.6)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#c0d8f0", height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        section_title("Hourly Activity by Operation Mode")
        fig = px.area(HOURLY_TREND, x='hour', y=['Active', 'Idle', 'Maintenance'], color_discrete_map=MODE_COLOR)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#c0d8f0", height=300)
        st.plotly_chart(fig, use_container_width=True)

    insight_box(
        "📡 <strong>Network Insight:</strong> The 6G network operates within a stable 1–50 ms latency window with packet loss contained below 5%. The near-uniform efficiency class distribution across ALL latency bands confirms that the current network envelope does not directly suppress efficiency.")

# --- TAB 3: EFFICIENCY ANALYSIS ---
with tab_id[2]:
    col_e, col_f = st.columns(2)
    with col_e:
        section_title("Efficiency Class by Latency Band")
        fig = px.bar(LATENCY_BAND, x='band', y=['High %', 'Medium %', 'Low %'], color_discrete_map=EFF_COLOR)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#c0d8f0", height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col_f:
        section_title("Error Rate vs Production Speed")
        fig = px.scatter(SCATTER_DATA, x='error', y='speed', color='eff', color_discrete_map=EFF_COLOR)
        fig.add_vline(x=2, line_dash="dash", line_color=GREEN, annotation_text="Eff. threshold")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#c0d8f0", height=300)
        st.plotly_chart(fig, use_container_width=True)

    section_title("Feature Correlation with Efficiency Status")
    fig = px.bar(CORR_DATA, x='corr', y='feature', orientation='h',
                 color='corr', color_continuous_scale=[[0, RED], [0.5, "rgba(100,150,200,0.4)"], [1, GREEN]])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#c0d8f0", height=300)
    st.plotly_chart(fig, use_container_width=True)
    insight_box(
        "🔍 <strong>Dominant Signal:</strong> Error Rate correlation of −0.604 dwarfs all other features. Production Speed (+0.334) is the only other meaningful predictor.")

    section_title("Efficiency Capability Radar")

    radar_fig = go.Figure()

    for cat in ["High", "Medium", "Low"]:
        radar_fig.add_trace(
            go.Scatterpolar(
                r=RADAR_DATA[cat].tolist(),
                theta=RADAR_DATA["metric"].tolist(),
                fill="toself",
                name=cat,
                line=dict(color=EFF_COLOR[cat], width=2)
            )
        )

    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#c0d8f0",
        height=400
    )

    st.plotly_chart(radar_fig, use_container_width=True)

# --- TAB 4: QUALITY & ERROR IMPACT ---
with tab_id[3]:
    col_g, col_h = st.columns(2)
    with col_g:
        section_title("Avg Error Rate by Efficiency Class")
        for _, row in EFF_METRICS.iterrows():
            st.write(f"{row['status']}: {row['error']}%")
            st.progress(row['error'] / 15.0)
        insight_box(
            "⚠️ The error rate difference between High (1.01%) and Low (8.93%) efficiency is 8.8× — the most decisive gap.",
            RED)

    with col_h:
        section_title("Avg Defect Rate by Packet Loss Band")
        fig = px.bar(PL_BAND, x='band', y='defect', color='defect', color_continuous_scale='Blues')
        fig.update_layout(yaxis_range=[4.8, 5.1], paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font_color="#c0d8f0", height=300)
        st.plotly_chart(fig, use_container_width=True)

    section_title("Error Rate × Latency Band × Operation Mode")
    heatmap_data = [
        {"Mode": "Active", "0-15ms": "7.49%", "15-30ms": "7.51%", "30-45ms": "7.50%", "45-50ms": "7.49%"},
        {"Mode": "Idle", "0-15ms": "7.52%", "15-30ms": "7.53%", "30-45ms": "7.52%", "45-50ms": "7.51%"},
        {"Mode": "Maintenance", "0-15ms": "7.53%", "15-30ms": "7.55%", "30-45ms": "7.54%", "45-50ms": "7.53%"},
    ]
    st.table(pd.DataFrame(heatmap_data))

# --- TAB 5: 6G OPTIMIZATION ---
with tab_id[4]:
    section_title("🎯 KPI Performance Dashboard")
    kpi_cols2 = st.columns(5)
    with kpi_cols2[0]: kpi_card("Error Rate - High", "1.01%", "Target: < 2.0% ✅", accent=True)
    with kpi_cols2[1]: kpi_card("Prod Speed - High", "450.8", "Target: > 400 ✅", accent=True)
    with kpi_cols2[2]: kpi_card("Avg Latency", "25.6 ms", "Target: < 30 ms ✅", accent=True)
    with kpi_cols2[3]: kpi_card("Packet Loss", "2.49%", "Target: < 2.0% ⚠️", warn=True)
    with kpi_cols2[4]: kpi_card("High Eff Rate", "3.0%", "Target: > 25% ⚠️", warn=True)

    section_title("⚡ Strategic Recommendations")
    rec_cols = st.columns(2)
    with rec_cols[0]:
        recommendation_box("🎯 Priority 1 — Error Rate Control",
                           "Reduce operational error rate below 2.0% to achieve High efficiency. Implement real-time monitoring with alerts at 3% and escalation at 5%.")
        recommendation_box("🌐 Priority 3 — Network Stress Testing",
                           "Extend testing beyond 50 ms latency and 5% packet loss to characterise the true efficiency collapse threshold.")
    with rec_cols[1]:
        recommendation_box("🚀 Priority 2 — Production Speed Floor",
                           "Set machine-level speed alerts at 380 units/hr as an early degradation signal. High-efficiency machines sustain 400–499 units/hr.")
        recommendation_box("🔧 Priority 4 — 6G Network Slicing",
                           "Implement QoS-based network slicing to prioritise Active-mode, high-error machines during peak production.")

    st.markdown(f"""
        <div style="background:rgba(0,212,255,0.05); border:1px solid {BORDER}; border-radius:12px; padding:20px; margin-top:16px;">
            <div style="font-size:13px; font-weight:700; color:{CYAN}; margin-bottom:8px; letter-spacing:1px;">📋 EXECUTIVE SUMMARY</div>
            <p style="font-size:13px; color:rgba(200,230,255,0.85); line-height:1.8; margin:0;">
                Across <strong>100,000 records</strong> from <strong>50 industrial machines</strong>, the 6G network at Thales Group is operating within its designed envelope. 
                The dominant efficiency driver is <span style="color:{RED}">Error Rate</span> (correlation −0.60). 
                The <span style="color:{RED}">77.8% Low-efficiency baseline</span> represents the primary operational challenge requiring urgent systemic intervention.
            </p>
        </div>
    """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(f"""
    <div style="text-align:center; color:rgba(100,150,200,0.25); font-size:10px; padding:20px 0; letter-spacing:2px; border-top:1px solid {BORDER}; margin-top:20px;">
        THALES GROUP · 6G SMART FACTORY ANALYTICS · 100,000 RECORDS · 50 MACHINES · FY 2025
    </div>
""", unsafe_allow_html=True)
