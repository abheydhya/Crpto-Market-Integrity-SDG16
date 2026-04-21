import streamlit as st
import plotly.graph_objects as go
from anomaly_detector import fetch_and_analyze
import google.generativeai as genai
import os
from dotenv import load_dotenv, dotenv_values

base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, ".env"), override=True)

# Parse file explicitly to bypass Streamlit environment caching issues
env_dict = dotenv_values(os.path.join(base_dir, ".env"))
api_key = env_dict.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Market Integrity Monitor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom CSS — dark-mode premium styling
# ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Import Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
        border-right: 1px solid #21262d;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMarkdown {
        color: #c9d1d9 !important;
    }

    /* ── Header banner ── */
    .main-header {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #1a1e2e 100%);
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 28px 36px;
        margin-bottom: 24px;
        box-shadow: 0 4px 24px rgba(0,0,0,.45);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header p {
        margin: 6px 0 0;
        color: #8b949e;
        font-size: .95rem;
    }

    /* ── Metric cards row ── */
    .metric-row {
        display: flex;
        gap: 16px;
        margin-bottom: 24px;
    }
    .metric-card {
        flex: 1;
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 18px 22px;
        box-shadow: 0 2px 10px rgba(0,0,0,.30);
    }
    .metric-card .label {
        color: #8b949e;
        font-size: .78rem;
        text-transform: uppercase;
        letter-spacing: .6px;
        margin-bottom: 4px;
    }
    .metric-card .value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #e6edf3;
    }
    .metric-card .value.alert {
        color: #f85149;
    }
    .metric-card .value.safe {
        color: #3fb950;
    }

    /* ── Anomaly table header ── */
    .anomaly-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 28px;
        margin-bottom: 10px;
    }
    .anomaly-header h3 {
        margin: 0;
        color: #f85149;
        font-weight: 700;
    }

    /* ── Footer ── */
    .footer-note {
        text-align: center;
        color: #484f58;
        font-size: .75rem;
        margin-top: 40px;
        padding-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ Scanner Settings")
    st.markdown("---")

    symbol = st.selectbox(
        "Select Coin Pair",
        options=["XRP/USDT", "BTC/USDT", "ETH/USDT"],
        index=0,
    )

    st.markdown("")
    run_scan = st.button("🔍  Run Scan", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown(
        "<div style='color:#8b949e; font-size:.8rem;'>"
        "Powered by <strong>ccxt</strong> · Binance<br>"
        "Z-Score threshold: <strong>3.0</strong><br>"
        "Rolling window: <strong>20 min</strong>"
        "</div>",
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────
st.markdown(
    """
    <div class="main-header">
        <h1>🛡️ Crypto Market Integrity Monitor</h1>
        <p>Real-time volume anomaly detection · SDG 16 — Peace, Justice &amp; Strong Institutions</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# Main Logic
# ──────────────────────────────────────────────
if run_scan:
    with st.spinner(f"Fetching live {symbol} data from Binance…"):
        df = fetch_and_analyze(symbol)

    # Drop NaN rows produced by rolling window
    df_clean = df.dropna(subset=["z_score"]).reset_index(drop=True)
    anomalies = df_clean[df_clean["is_anomaly"]]

    # ── Metric Cards ──
    latest_close = df_clean["close"].iloc[-1]
    total_vol = df_clean["volume"].sum()
    anomaly_count = len(anomalies)
    max_z = df_clean["z_score"].max()

    alert_cls = "alert" if anomaly_count > 0 else "safe"
    status_icon = "🚨" if anomaly_count > 0 else "🟢"

    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="label">Coin Pair</div>
                <div class="value">{symbol}</div>
            </div>
            <div class="metric-card">
                <div class="label">Latest Close</div>
                <div class="value">${latest_close:,.4f}</div>
            </div>
            <div class="metric-card">
                <div class="label">Total Volume</div>
                <div class="value">{total_vol:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="label">Max Z-Score</div>
                <div class="value">{max_z:.2f}</div>
            </div>
            <div class="metric-card">
                <div class="label">Anomalies Found</div>
                <div class="value {alert_cls}">{status_icon} {anomaly_count}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Plotly Volume Chart ──
    bar_colors = [
        "rgba(248,81,73,0.6)" if row.is_anomaly else "#58a6ff"
        for _, row in df_clean.iterrows()
    ]

    fig = go.Figure()

    # Volume bars
    fig.add_trace(
        go.Bar(
            x=df_clean["timestamp"],
            y=df_clean["volume"],
            marker_color=bar_colors,
            marker_line_width=0,
            name="Volume",
            hovertemplate=(
                "<b>%{x|%H:%M:%S}</b><br>"
                "Volume: %{y:,.2f}<br>"
                "<extra></extra>"
            ),
        )
    )

    # Anomaly markers — red ✕ scatter on anomalous bars
    if not anomalies.empty:
        fig.add_trace(
            go.Scatter(
                x=anomalies["timestamp"],
                y=anomalies["volume"],
                mode="markers",
                marker=dict(
                    symbol="x",
                    size=14,
                    color="#ff4d4f",
                    line=dict(width=2, color="#ff4d4f"),
                ),
                name="Anomaly",
                hovertemplate=(
                    "<b>🚨 ANOMALY</b><br>"
                    "Time: %{x|%H:%M:%S}<br>"
                    "Volume: %{y:,.2f}<br>"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        font=dict(family="Inter, sans-serif", color="#c9d1d9"),
        title=dict(
            text=f"{symbol}  ·  Volume Over Time",
            font=dict(size=18, color="#e6edf3"),
            x=0.01,
        ),
        xaxis=dict(
            title="Timestamp",
            gridcolor="#21262d",
            showgrid=True,
        ),
        yaxis=dict(
            title="Volume",
            gridcolor="#21262d",
            showgrid=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        bargap=0.15,
        hovermode="x unified",
        height=480,
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Anomaly Details Table ──
    if not anomalies.empty:
        st.markdown(
            """
            <div class="anomaly-header">
                <h3>🚨 Detected Anomalies</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        display_cols = ["timestamp", "close", "volume", "z_score"]
        anomaly_display = anomalies[display_cols].copy()
        anomaly_display.columns = ["Timestamp", "Close Price", "Volume", "Z-Score"]
        anomaly_display["Z-Score"] = anomaly_display["Z-Score"].round(2)

        st.dataframe(
            anomaly_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Timestamp": st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm:ss"),
                "Close Price": st.column_config.NumberColumn(format="$%.4f"),
                "Volume": st.column_config.NumberColumn(format="%.2f"),
                "Z-Score": st.column_config.NumberColumn(format="%.2f"),
            },
        )

        # --- NEW GEMINI AI INTEGRATION ---
        st.divider()
        st.subheader("🤖 Gemini AI Threat Analysis")
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # We feed the stats to Gemini to get a report
                max_vol = anomalies['volume'].max()
                max_z = anomalies['z_score'].max()
                
                prompt = f"""
                Act as a quantitative finance regulatory expert. We just detected a severe market anomaly for {symbol}. 
                The trading volume suddenly spiked to {max_vol} with a statistical Z-Score of {max_z} (normal is < 3). 
                Write a brief, 3-sentence threat report explaining why this specific data indicates potential market manipulation (like wash trading) and why it is dangerous for retail investors.
                """
                
                with st.spinner("Gemini AI is analyzing the anomaly..."):
                    response = model.generate_content(prompt)
                    st.info(response.text)
            except Exception as e:
                st.error(f"AI Analysis Error: Check your API key. ({e})")

    else:
        st.success("🟢  Market looks normal — no volume anomalies detected in this window.")

else:
    # ── Idle state ──
    st.markdown(
        """
        <div style="text-align:center; padding:80px 20px; color:#8b949e;">
            <p style="font-size:3rem; margin-bottom:8px;">🔎</p>
            <p style="font-size:1.1rem; font-weight:600; color:#c9d1d9;">
                Select a coin pair and click <em>Run Scan</em> to begin analysis
            </p>
            <p style="font-size:.85rem;">
                The scanner fetches the last 100 minutes of 1-minute OHLCV data from Binance
                and flags volume spikes with Z-Score &gt; 3.0
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Footer ──
st.markdown(
    '<div class="footer-note">Crypto Market Integrity Monitor · SDG 16 · Built with Streamlit &amp; Plotly</div>',
    unsafe_allow_html=True,
)
