import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils import generate_transaction
import io

# Set page configuration
st.set_page_config(
    page_title="AEGIS PRIME | Advanced Fraud Intelligence",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed" # Modern full-screen feel
)

# INNOVATIVE UI: High-End "Cyber-Neon" Dashboard with Custom Components
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    * { font-family: 'Outfit', sans-serif; }
    
    .stApp {
        background-color: #05070a;
        background-image: 
            radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.05) 0, transparent 50%),
            radial-gradient(at 50% 0%, rgba(129, 140, 248, 0.05) 0, transparent 50%),
            radial-gradient(at 100% 0%, rgba(236, 72, 153, 0.05) 0, transparent 50%);
        color: #ffffff;
    }

    /* Modern Title Branding */
    .hero-container {
        padding: 2rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 2.5rem;
    }
    
    .hero-logo {
        font-weight: 800;
        font-size: 2.2rem;
        letter-spacing: -1px;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .hero-logo span {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* NEON KPI CARDS */
    .kpi-card {
        background: rgba(13, 17, 23, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 1.25rem;
        padding: 1.5rem;
        text-align: left;
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0, 242, 254, 0.5), transparent);
    }

    .kpi-label {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0.5rem 0;
        font-family: 'JetBrains Mono', monospace;
    }

    /* INTELLIGENCE FEED */
    .feed-container {
        max-height: 600px;
        overflow-y: auto;
        padding-right: 10px;
    }
    
    .feed-item {
        background: #0d1117;
        border-radius: 1rem;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.03);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .feed-item:hover {
        background: #161b22;
        border-color: rgba(56, 189, 248, 0.2);
        transform: scale(1.01);
    }

    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
    }
    
    .badge-fraud { background: rgba(239, 68, 68, 0.15); color: #ff4d4d; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-genuine { background: rgba(16, 185, 129, 0.15); color: #00ff9d; border: 1px solid rgba(16, 185, 129, 0.3); }

    /* AUDIT REGISTRY TABLE CUSTOMIZATION */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 1rem;
        overflow: hidden;
    }

    /* CONTROL PANEL */
    .control-panel {
        background: #0d1117;
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid rgba(255,255,255,0.05);
    }

    /* Remove standard streamlit header */
    header { visibility: hidden; }
    .block-container { padding-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

# 1. State Management
if 'history' not in st.session_state: st.session_state.history = []
if 'is_running' not in st.session_state: st.session_state.is_running = False

# --- TOP HERO BAR ---
st.markdown(f"""
    <div class="hero-container">
        <div class="hero-logo">💠 <span>AEGIS</span> PRIME</div>
        <div style="display: flex; gap: 20px; align-items: center;">
            <div style="text-align: right;">
                <div style="font-size: 0.7rem; color: #64748b; font-weight: 800; letter-spacing: 1px;">ENGINE STATUS</div>
                <div style="font-size: 0.9rem; color: {'#00ff9d' if st.session_state.is_running else '#64748b'};">
                    {'● ACTIVE SCANNING' if st.session_state.is_running else '○ SYSTEM STANDBY'}
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# 2. Control Row
c_ctrl1, c_ctrl2, c_ctrl3 = st.columns([1, 2, 1])
with c_ctrl1:
    if st.button("ACTIVATE SYSTEM" if not st.session_state.is_running else "DEACTIVATE", use_container_width=True):
        st.session_state.is_running = not st.session_state.is_running
with c_ctrl2:
    threshold = st.select_slider("Risk Sensitivity Threshold", options=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], value=0.5)
with c_ctrl3:
    if st.session_state.history:
        csv = pd.DataFrame(st.session_state.history).to_csv(index=False).encode('utf-8')
        st.download_button("💾 EXPORT AUDIT", csv, "aegis_prime_audit.csv", "text/csv", use_container_width=True)

# 3. Simulation & Backend
if st.session_state.is_running:
    new_tx = generate_transaction()
    new_tx['Threshold'] = threshold
    try:
        response = requests.post("http://127.0.0.1:8000/predict", json=new_tx)
        if response.status_code == 200:
            result = response.json()
            new_tx.update(result)
            new_tx['Timestamp'] = datetime.now().strftime("%H:%M:%S")
            st.session_state.history.append(new_tx)
            if len(st.session_state.history) > 150: st.session_state.history.pop(0)
    except Exception:
        st.error("AEGIS Core connection severed.")

# 4. Intelligence Grid
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    
    # --- KPI ROW ---
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Thruput</div><div class="kpi-value">{len(df)}</div></div>""", unsafe_allow_html=True)
    with k2:
        fraud_count = len(df[df['prediction'] == 'Fraud'])
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label" style="color:#ff4d4d">Breaches</div><div class="kpi-value" style="color:#ff4d4d">{fraud_count}</div></div>""", unsafe_allow_html=True)
    with k3:
        anom_count = len(df[df['is_anomaly']])
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label" style="color:#fbbf24">Anomalies</div><div class="kpi-value" style="color:#fbbf24">{anom_count}</div></div>""", unsafe_allow_html=True)
    with k4:
        avg_risk = df['risk_score'].mean()
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">System Risk</div><div class="kpi-value">{avg_risk:.1f}%</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- MAIN ANALYTICS GRID ---
    col_main_left, col_main_right = st.columns([1.2, 2], gap="large")

    with col_main_left:
        st.markdown("<h3 style='font-size: 1rem; color: #64748b; letter-spacing: 2px;'>LIVE INTEL STREAM</h3>", unsafe_allow_html=True)
        
        # Fixed-height scrollable container to prevent page jumping
        with st.container(height=500):
            if st.session_state.history:
                for tx in reversed(st.session_state.history[-20:]):
                    is_f = tx['prediction'] == 'Fraud'
                    badge = "badge-fraud" if is_f else "badge-genuine"
                    st.markdown(f"""
                        <div class="feed-item">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <span class="status-badge {badge}">{tx['prediction']}</span>
                                <code style="color: #4b5563; font-size: 0.8rem;">{tx['Timestamp']}</code>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: #94a3b8;">Amount</span>
                                <span style="font-weight: 600;">${tx['Amount']:.2f}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: #94a3b8;">Risk Factor</span>
                                <span style="color: {'#ff4d4d' if is_f else '#00ff9d'}; font-weight: 800;">{tx['risk_score']}%</span>
                            </div>
                            <div style="font-size: 0.8rem; color: #4b5563; margin-top: 5px;">
                                Loc: {tx['Location']} | Merch: {tx['MerchantType']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Awaiting live stream...")

    with col_main_right:
        # 1. NETWORK RISK PRESSURE (Clean splined area chart)
        st.markdown("<h3 style='font-size: 1rem; color: #64748b; letter-spacing: 2px;'>NETWORK RISK PRESSURE</h3>", unsafe_allow_html=True)
        fig_area = go.Figure()
        fig_area.add_trace(go.Scatter(
            x=df['Timestamp'], y=df['risk_score'],
            fill='tozeroy', mode='lines',
            line=dict(width=3, color='#00f2fe'),
            fillcolor='rgba(0, 242, 254, 0.05)'
        ))
        fig_area.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=0, l=0, r=0), height=250,
            xaxis=dict(showgrid=False, color='#4b5563'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', color='#4b5563')
        )
        st.plotly_chart(fig_area, use_container_width=True)

        # 2. GEOSPATIAL THREAT ANALYSIS
        st.markdown("<h3 style='font-size: 1rem; color: #64748b; letter-spacing: 2px; margin-top: 1rem;'>GEOSPATIAL THREAT ANALYSIS</h3>", unsafe_allow_html=True)
        geo_stats = df.groupby('Location').agg({'risk_score': 'mean', 'prediction': 'count'}).reset_index()
        fig_geo = px.bar(
            geo_stats, x='Location', y='prediction', color='risk_score',
            color_continuous_scale='RdBu_r', 
            labels={'prediction': 'Events', 'risk_score': 'Risk %'}
        )
        fig_geo.update_layout(
            height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#94a3b8', margin=dict(t=20, b=0, l=0, r=0),
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)')
        )
        st.plotly_chart(fig_geo, use_container_width=True)

        # 3. BEHAVIORAL FINGERPRINT & TEMPORAL FRAUD PULSE (Side-by-Side)
        if len(df) > 0:
            c_radar, c_pulse = st.columns(2)
            
            with c_radar:
                st.markdown("<h3 style='font-size: 0.9rem; color: #64748b; letter-spacing: 2px; margin-top: 1.5rem;'>BEHAVIORAL FINGERPRINT</h3>", unsafe_allow_html=True)
                latest_tx = df.iloc[-1]
                categories = ['Amount', 'Velocity', 'Distance', 'Risk', 'Failed']
                radar_values = [
                    min(latest_tx['Amount']/500, 1.0),
                    min(latest_tx['Velocity24h']/20, 1.0),
                    min(latest_tx['DistanceFromHome']/2000, 1.0),
                    latest_tx['risk_score']/100,
                    min(latest_tx['FailedAttempts']/3, 1.0)
                ]
                
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=radar_values,
                    theta=categories,
                    fill='toself',
                    line_color='#00f2fe',
                    fillcolor='rgba(0, 242, 254, 0.2)'
                ))
                fig_radar.update_layout(
                    polar=dict(
                        bgcolor='rgba(0,0,0,0)',
                        radialaxis=dict(visible=True, showticklabels=False, gridcolor='rgba(255,255,255,0.05)'),
                        angularaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#94a3b8')
                    ),
                    showlegend=False,
                    height=280,
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=30, b=30, l=30, r=30)
                )
                st.plotly_chart(fig_radar, use_container_width=True)

            with c_pulse:
                st.markdown("<h3 style='font-size: 0.9rem; color: #64748b; letter-spacing: 2px; margin-top: 1.5rem;'>TEMPORAL FRAUD PULSE</h3>", unsafe_allow_html=True)
                fig_sun = px.sunburst(
                    df[df['risk_score'] > 20], 
                    path=['MerchantType', 'Location'], 
                    values='risk_score',
                    color='risk_score',
                    color_continuous_scale='YlOrRd'
                )
                fig_sun.update_layout(
                    margin=dict(t=0, l=0, r=0, b=0),
                    height=280,
                    paper_bgcolor='rgba(0,0,0,0)',
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_sun, use_container_width=True)

    # --- BOTTOM SECTION: THREAT TOPOGRAPHY & AUDIT REGISTRY ---
    st.divider()
    
    col_bot_left, col_bot_mid, col_bot_right = st.columns([1.2, 1.2, 1.5], gap="medium")
    
    with col_bot_left:
        # 5. NEW & UNIQUE: RISK SCATTER VELOCITY
        st.markdown("<h3 style='font-size: 1rem; color: #64748b; letter-spacing: 2px;'>RISK VELOCITY CLUSTERS</h3>", unsafe_allow_html=True)
        fig_scatter = px.scatter(
            df, x='Amount', y='Velocity24h', color='prediction',
            size='risk_score', hover_data=['Location'],
            color_discrete_map={'Fraud': '#ef4444', 'Genuine': '#10b981'}
        )
        fig_scatter.update_layout(
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=0, b=0, l=0, r=0), height=280,
            xaxis=dict(showgrid=False, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_bot_mid:
        # 6. INCIDENT TYPE DISTRIBUTION (Threat Topography)
        st.markdown("<h3 style='font-size: 1rem; color: #64748b; letter-spacing: 2px;'>THREAT TOPOGRAPHY</h3>", unsafe_allow_html=True)
        dist_data = pd.DataFrame([
            {"Type": "Genuine", "Value": len(df[(df['prediction'] == 'Genuine') & (~df['is_anomaly'])])},
            {"Type": "Anomalous", "Value": len(df[df['is_anomaly']])},
            {"Type": "Fraud", "Value": len(df[df['prediction'] == 'Fraud'])}
        ])
        
        fig_donut = px.pie(
            dist_data, values='Value', names='Type', hole=0.7,
            color='Type', color_discrete_map={'Genuine': '#10b981', 'Anomalous': '#fbbf24', 'Fraud': '#ef4444'}
        )
        fig_donut.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, b=0, l=0, r=0), height=280)
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_bot_right:
        st.markdown("<h3 style='font-size: 1rem; color: #64748b; letter-spacing: 2px;'>CENTRAL AUDIT REGISTRY</h3>", unsafe_allow_html=True)
        
        # Fixed the segmented_control error by using radio with horizontal=True
        filter_choice = st.radio("registry_filter", ["ALL EVENTS", "FRAUD ONLY", "ANOMALIES"], horizontal=True, label_visibility="collapsed")
        
        audit_df = df.copy()
        if filter_choice == "FRAUD ONLY": audit_df = audit_df[audit_df['prediction'] == 'Fraud']
        elif filter_choice == "ANOMALIES": audit_df = audit_df[audit_df['is_anomaly']]
        
        st.dataframe(
            audit_df[['Timestamp', 'Amount', 'Location', 'MerchantType', 'risk_score', 'prediction', 'is_anomaly']].iloc[::-1],
            use_container_width=True,
            hide_index=True,
            column_config={
                "risk_score": st.column_config.ProgressColumn("Risk Factor", format="%d%%", min_value=0, max_value=100),
                "prediction": st.column_config.TextColumn("Verdict"),
                "is_anomaly": st.column_config.CheckboxColumn("Anomaly Flag")
            }
        )

else:
    st.info("Aegis Prime initialized. Activate system to begin real-time neural processing.")

# Auto-refresh loop
if st.session_state.is_running:
    time.sleep(3.0)
    st.rerun()
