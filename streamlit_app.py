import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Churn-a-nator · iD Mobile",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PALETTE ──────────────────────────────────────────────────
TEAL        = "#0A9396"
TEAL_LIGHT  = "#94D2BD"
TEAL_PALE   = "#E0F4F4"
SLATE       = "#2D3748"
CHARCOAL    = "#1A202C"
MUTED       = "#718096"
BG          = "#F7F8FA"
WHITE       = "#FFFFFF"
RED         = "#C0392B"
RED_PALE    = "#FEE2E2"
AMBER       = "#E8A020"
AMBER_PALE  = "#FEF3C7"
GREEN       = "#1A8754"
BORDER      = "#E2E8F0"

HIGH_RISK   = 0.40
MEDIUM_RISK = 0.20

SCORE_WEIGHTS = {
    'contract_mtm':     3,
    'tenure_early':     3,
    'no_tech_support':  2,
    'electronic_check': 2,
    'fibre_optic':      1,
    'senior_citizen':   1,
}
MAX_SCORE = sum(SCORE_WEIGHTS.values())  # 12

def calc_risk_score(row):
    score = 0
    if row['Contract']        == 'Month-to-month':   score += SCORE_WEIGHTS['contract_mtm']
    if row['tenure']          <= 12:                 score += SCORE_WEIGHTS['tenure_early']
    if row['TechSupport']     == 'No':               score += SCORE_WEIGHTS['no_tech_support']
    if row['PaymentMethod']   == 'Electronic check': score += SCORE_WEIGHTS['electronic_check']
    if row['InternetService'] == 'Fiber optic':      score += SCORE_WEIGHTS['fibre_optic']
    if str(row['SeniorCitizen']) == '1':             score += SCORE_WEIGHTS['senior_citizen']
    return score

def score_label(score):
    if score >= 9: return f"HIGH {score}/{MAX_SCORE}"
    if score >= 6: return f"MED {score}/{MAX_SCORE}"
    return f"LOW {score}/{MAX_SCORE}"

# ── SVG ICON LIBRARY ─────────────────────────────────────────
# Solid-colour inline SVGs sized at 18px, colour-matched to palette
def svg(path_d, color, size=18, vb="0 0 24 24"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="{vb}" fill="{color}" style="flex-shrink:0;margin-top:1px"><path d="{path_d}"/></svg>'

# Icon paths (Material-style solid fills)
ICONS = {
    # Insight icons
    "trend_down":   "M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z",
    "contract":     "M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z",
    "payment":      "M20 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z",
    "silent":       "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z",
    "warning":      "M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z",
    "signal":       "M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z",
    "revenue":      "M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z",
    # Action icons
    "onboard":      "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z",
    "upgrade":      "M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z",
    "outreach":     "M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z",
    "investigate":  "M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z",
    "fibre":        "M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z",
    # Priority dots
    "dot_high":     "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z",
    # Section heading icons
    "bar_chart":    "M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z",
    "eye":          "M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z",
    "target":       "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z",
    "lightbulb":    "M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7z",
    "rocket":       "M12 2.5s4.5 2.04 4.5 10.5c0 2.49-1.04 4.71-2.7 6.3L12 21l-1.8-1.7C8.54 17.71 7.5 15.49 7.5 13 7.5 4.54 12 2.5 12 2.5zm0 7c-.83 0-1.5.67-1.5 1.5S11.17 12.5 12 12.5s1.5-.67 1.5-1.5S12.83 9.5 12 9.5zM5 11.5c0-1.53.3-2.98.84-4.31L4.27 5.62C3.48 7.26 3 9.13 3 11.12c0 4.5 2.53 8.41 6.24 10.44l1.44-1.47C7.17 18.5 5 15.21 5 11.5zm14 0c0 3.71-2.17 6.96-5.31 8.56l1.44 1.47c3.71-2.03 6.24-5.94 6.24-10.44 0-2-.48-3.87-1.28-5.51l-1.56 1.57c.53 1.33.47 2.82.47 4.35z",
}

def icon_html(key, color=TEAL, size=18):
    return svg(ICONS[key], color, size)

def dot_html(color, size=10):
    """Small solid circle for priority indicators"""
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 10 10"><circle cx="5" cy="5" r="5" fill="{color}"/></svg>'


# ── GLOBAL CSS ───────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{ background-color: {BG}; }}
  #MainMenu, footer, header {{ visibility: hidden; }}
  html, body, [class*="css"] {{
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color: {SLATE};
  }}

  /* Header */
  .dash-header {{
    background: {CHARCOAL};
    padding: 1.1rem 2rem;
    border-radius: 10px;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .dash-header h1 {{
    color: {WHITE}; font-size: 1.25rem; font-weight: 700;
    margin: 0; letter-spacing: 0.02em;
  }}
  .dash-header span {{
    color: {TEAL}; font-size: 0.8rem; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
  }}

  /* Section heading */
  .section-heading {{
    font-size: 1.1rem; font-weight: 700; color: {CHARCOAL};
    margin-bottom: 0.2rem; padding-bottom: 0.4rem;
    border-bottom: 2px solid {BORDER};
    display: flex; align-items: center; gap: 0.5rem;
  }}

  /* MRR Banner */
  .mrr-banner {{
    background: linear-gradient(135deg, {CHARCOAL} 0%, #2d3f52 100%);
    border-radius: 10px; padding: 1.3rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  }}
  .mrr-left {{ flex: 1; }}
  .mrr-eyebrow {{
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: {TEAL}; margin-bottom: 0.3rem;
    display: flex; align-items: center; gap: 0.4rem;
  }}
  .mrr-headline {{ font-size: 1.4rem; font-weight: 800; color: {WHITE}; line-height: 1.2; }}
  .mrr-sub {{ font-size: 0.82rem; color: #94A3B8; margin-top: 0.3rem; }}
  .mrr-stat {{
    text-align: center; padding: 0 1.4rem;
    border-left: 1px solid rgba(255,255,255,0.1);
  }}
  .mrr-stat .stat-val {{ font-size: 1.5rem; font-weight: 800; color: {WHITE}; }}
  .mrr-stat .stat-label {{
    font-size: 0.65rem; color: #94A3B8; text-transform: uppercase;
    letter-spacing: 0.07em; margin-top: 0.1rem;
  }}

  /* Formula box */
  .formula-box {{
    background: {TEAL_PALE}; border: 1px solid {TEAL};
    border-radius: 8px; padding: 0.65rem 1.2rem;
    margin-bottom: 0.5rem; display: flex;
    align-items: center; gap: 1.5rem; flex-wrap: wrap;
  }}
  .formula-label {{
    font-size: 0.7rem; font-weight: 700; color: {TEAL};
    text-transform: uppercase; letter-spacing: 0.08em; flex-shrink: 0;
  }}
  .formula-text {{ font-size: 0.88rem; color: {SLATE}; font-family: 'Courier New', monospace; }}
  .formula-note {{ font-size: 0.78rem; color: {MUTED}; font-style: italic; }}

  /* Score legend */
  .score-legend {{
    background: {WHITE}; border: 1px solid {BORDER};
    border-radius: 8px; padding: 0.6rem 1.1rem;
    margin-bottom: 0.6rem; display: flex;
    align-items: center; gap: 2rem; flex-wrap: wrap;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}
  .score-legend-label {{
    font-size: 0.7rem; font-weight: 700; color: {MUTED};
    text-transform: uppercase; letter-spacing: 0.08em; flex-shrink: 0;
  }}
  .score-legend-item {{ font-size: 0.82rem; color: {SLATE}; display:flex; align-items:center; gap:0.35rem; }}

  /* Chart cards */
  .chart-card {{
    background: {WHITE}; border-radius: 10px;
    padding: 1.1rem 1.1rem 0.4rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 0.5rem;
  }}
  .chart-title {{
    font-size: 0.78rem; font-weight: 700; color: {MUTED};
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.1rem;
  }}
  .chart-insight {{
    font-size: 0.82rem; color: {SLATE}; font-style: italic;
    margin-bottom: 0.6rem; line-height: 1.45;
  }}

  /* Risk callout */
  .risk-callout {{
    background: linear-gradient(135deg, #fff5f5 0%, {WHITE} 100%);
    border-left: 5px solid {RED}; border-radius: 10px;
    padding: 1.2rem 1.5rem; box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  }}
  .risk-label {{
    font-size: 0.68rem; font-weight: 700; color: {RED};
    letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.25rem;
    display: flex; align-items: center; gap: 0.35rem;
  }}
  .risk-number {{ font-size: 2.4rem; font-weight: 800; color: {RED}; line-height: 1; }}
  .risk-desc {{ font-size: 0.85rem; color: {SLATE}; margin-top: 0.3rem; line-height: 1.55; }}

  /* Insight cards */
  .insight-card {{
    background: {WHITE}; border-radius: 10px; padding: 0.9rem 1.1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06); border-left: 4px solid {TEAL};
    margin-bottom: 0.6rem; display: flex; align-items: flex-start; gap: 0.75rem;
  }}
  .insight-icon {{
    width: 32px; height: 32px; border-radius: 8px;
    background: {TEAL_PALE}; display: flex; align-items: center;
    justify-content: center; flex-shrink: 0;
  }}
  .insight-title {{ font-weight: 700; font-size: 0.86rem; color: {CHARCOAL}; }}
  .insight-body {{ font-size: 0.8rem; color: {MUTED}; margin-top: 0.12rem; line-height: 1.5; }}

  /* Action cards */
  .action-card {{
    background: {WHITE}; border-radius: 10px; padding: 0.9rem 1.1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    border-top: 3px solid {TEAL_LIGHT}; margin-bottom: 0.6rem;
    display: flex; align-items: flex-start; gap: 0.75rem;
  }}
  .action-icon {{
    width: 30px; height: 30px; border-radius: 6px;
    background: {TEAL_PALE}; display: flex; align-items: center;
    justify-content: center; flex-shrink: 0; margin-top: 0.1rem;
  }}
  .action-title {{ font-weight: 700; font-size: 0.86rem; color: {CHARCOAL}; }}
  .action-body {{ font-size: 0.8rem; color: {MUTED}; margin-top: 0.12rem; line-height: 1.5; }}

  /* Upload */
  .upload-box {{
    background: {WHITE}; border: 2px dashed {BORDER};
    border-radius: 12px; padding: 2rem 2.5rem 2.5rem;
    text-align: center; margin: 2rem auto; max-width: 500px;
  }}
  .upload-box h3 {{ color: {CHARCOAL}; font-size: 1rem; margin-bottom: 0.3rem; margin-top: 1rem; }}
  .upload-box p {{ color: {MUTED}; font-size: 0.83rem; }}

  .divider {{ border: none; border-top: 1px solid {BORDER}; margin: 1.5rem 0; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{ background: {CHARCOAL} !important; }}
  [data-testid="stSidebar"] * {{ color: {WHITE} !important; }}
  [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.1) !important; }}
</style>
""", unsafe_allow_html=True)


# ── PLOTLY HELPERS ────────────────────────────────────────────
def base_layout(height=270):
    return dict(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(family="Inter, Segoe UI, sans-serif", color=MUTED, size=11),
        xaxis=dict(showgrid=False, showline=False, tickfont=dict(size=10, color=MUTED)),
        yaxis=dict(gridcolor=BORDER, gridwidth=0.8, showline=False, tickfont=dict(size=10, color=MUTED)),
        showlegend=False,
        hoverlabel=dict(bgcolor=CHARCOAL, font_color=WHITE, font_size=12, bordercolor=CHARCOAL),
    )

def bar_color(val):
    if val >= HIGH_RISK:   return RED
    if val >= MEDIUM_RISK: return AMBER
    return TEAL


# ── LOGO HELPER ──────────────────────────────────────────────
def load_image_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None


# ── HEADER ───────────────────────────────────────────────────
logo_b64 = load_image_b64("logo.png") or load_image_b64("logo_big.png")
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:42px;width:42px;border-radius:50%;object-fit:cover;">' if logo_b64 else ""

st.markdown(f"""
<div class="dash-header">
  <div style="display:flex;align-items:center;gap:1rem;">
    {logo_html}
    <h1>Churn-a-nator >> Terminating Churn</h1>
  </div>
  <span>iD Mobile &nbsp;·&nbsp; Project Lantern</span>
</div>
""", unsafe_allow_html=True)


# ── UPLOAD ───────────────────────────────────────────────────
upload_slot = st.empty()
with upload_slot.container():
    upload_logo_b64 = load_image_b64("logo_big.png") or load_image_b64("logo.png")
    upload_logo_html = f'<img src="data:image/png;base64,{upload_logo_b64}" style="width:120px;height:120px;object-fit:contain;margin-bottom:0.5rem;">' if upload_logo_b64 else ""
    st.markdown(f"""
    <div class="upload-box">
      {upload_logo_html}
      <h3>Upload your churn dataset</h3>
      <p>CSV file - IBM Telco Churn format</p>
    </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["csv"], label_visibility="collapsed")

if uploaded_file is None:
    st.stop()

upload_slot.empty()


# ── LOAD & PREP ──────────────────────────────────────────────
df = pd.read_csv(uploaded_file)
df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['tenure_group'] = pd.cut(
    df['tenure'], bins=[0, 12, 24, 48, 72],
    labels=['0–12 mo', '13–24 mo', '25–48 mo', '49–72 mo']
)
df['risk_score'] = df.apply(calc_risk_score, axis=1)


# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='padding:0.5rem 0 0.8rem'>
      <div style='font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:{TEAL};margin-bottom:0.25rem;'>iD Mobile</div>
      <div style='font-size:1rem;font-weight:700;color:white;'>Churn-a-nator</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.68rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:{TEAL};margin-bottom:0.5rem;'>Filters</div>", unsafe_allow_html=True)
    contract_filter  = st.selectbox("Contract Type",    ["All"] + sorted(df['Contract'].unique().tolist()))
    tech_filter      = st.selectbox("Tech Support",     ["All"] + sorted(df['TechSupport'].unique().tolist()))
    payment_filter   = st.selectbox("Payment Method",   ["All"] + sorted(df['PaymentMethod'].unique().tolist()))
    internet_filter  = st.selectbox("Internet Service", ["All"] + sorted(df['InternetService'].unique().tolist()))
    tenure_range     = st.slider("Tenure (months)", 0, 72, (0, 72))
    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:0.72rem;color:#94A3B8;line-height:1.8;'>
      High risk: ≥{HIGH_RISK:.0%} churn<br>
      Medium: {MEDIUM_RISK:.0%}–{HIGH_RISK:.0%} churn<br>
      Low: &lt;{MEDIUM_RISK:.0%} churn<br><br>
      Risk score out of {MAX_SCORE}.<br>
      High ≥9 · Medium 6–8 · Low &lt;6<br><br>
      Filters apply across all views.
    </div>
    """, unsafe_allow_html=True)


# ── APPLY FILTERS ─────────────────────────────────────────────
dff = df.copy()
if contract_filter  != "All": dff = dff[dff['Contract']        == contract_filter]
if tech_filter      != "All": dff = dff[dff['TechSupport']     == tech_filter]
if payment_filter   != "All": dff = dff[dff['PaymentMethod']   == payment_filter]
if internet_filter  != "All": dff = dff[dff['InternetService'] == internet_filter]
dff = dff[(dff['tenure'] >= tenure_range[0]) & (dff['tenure'] <= tenure_range[1])]


# ── KPIs ──────────────────────────────────────────────────────
total          = len(dff)
churned_count  = int(dff['Churn'].sum())
churn_rate     = dff['Churn'].mean()
retention_rate = 1 - churn_rate
avg_charge     = dff['MonthlyCharges'].mean()
mrr_at_risk    = dff[dff['Churn'] == 1]['MonthlyCharges'].sum()

high_risk = dff[(dff['Contract'] == 'Month-to-month') & (dff['TechSupport'] == 'No') & (dff['tenure'] <= 12)]
hr_rate  = high_risk['Churn'].mean() if len(high_risk) else 0
hr_count = len(high_risk)
hr_mrr   = high_risk[high_risk['Churn'] == 1]['MonthlyCharges'].sum()

fibre_risk = dff[(dff['InternetService'] == 'Fiber optic') & (dff['Contract'] == 'Month-to-month')]
fr_rate  = fibre_risk['Churn'].mean() if len(fibre_risk) else 0
fr_count = len(fibre_risk)
fr_mrr   = fibre_risk[fibre_risk['Churn'] == 1]['MonthlyCharges'].sum()

alert_icon = icon_html("warning", TEAL, 14)

# ── MRR BANNER ───────────────────────────────────────────────
st.markdown(f"""
<div class="mrr-banner">
  <div class="mrr-left">
    <div class="mrr-eyebrow">{alert_icon} Revenue at Risk · Current Filtered View</div>
    <div class="mrr-headline">£{mrr_at_risk:,.0f} in monthly recurring revenue has already churned</div>
    <div class="mrr-sub">
      {churned_count:,} churned customers at an average of £{avg_charge:.0f}/mo.
      High-risk cohort (month-to-month · no support · 0–12 mo) accounts for £{hr_mrr:,.0f} of this.
    </div>
  </div>
  <div class="mrr-stat"><div class="stat-val">{churn_rate:.1%}</div><div class="stat-label">Churn Rate</div></div>
  <div class="mrr-stat"><div class="stat-val">{retention_rate:.1%}</div><div class="stat-label">Retention Rate</div></div>
  <div class="mrr-stat"><div class="stat-val">{churned_count:,}</div><div class="stat-label">Churned</div></div>
  <div class="mrr-stat"><div class="stat-val">{total:,}</div><div class="stat-label">In View</div></div>
</div>
""", unsafe_allow_html=True)

# ── FORMULA BOX ──────────────────────────────────────────────
st.markdown(f"""
<div class="formula-box">
  <span class="formula-label">Key Formulas</span>
  <span class="formula-text">Churn Rate = Customers lost ÷ Customers at start of period × 100</span>
  <span class="formula-text">&nbsp;·&nbsp;</span>
  <span class="formula-text">Retention Rate = 1 − Churn Rate</span>
  <span class="formula-note">Tracked monthly to identify trends early</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# VIEW 1 – WHERE IS CHURN CONCENTRATED
# ════════════════════════════════════════════════════════════
st.markdown(f"<div class='section-heading'>{icon_html('bar_chart', TEAL, 18)} View 1 &nbsp;·&nbsp; Where is the churn happening?</div>", unsafe_allow_html=True)

v1c1, v1c2 = st.columns(2)

with v1c1:
    d = dff.groupby('tenure_group', observed=True).agg(
        churn_rate=('Churn', 'mean'), count=('Churn', 'count'), churned=('Churn', 'sum')
    ).reset_index()
    d['pct'] = (d['churn_rate'] * 100).round(1)
    fig = go.Figure(go.Bar(
        x=d['tenure_group'].astype(str), y=d['pct'],
        marker_color=[bar_color(v) for v in d['churn_rate']],
        text=[f"{v}%" for v in d['pct']], textposition='outside',
        textfont=dict(size=11, color=CHARCOAL),
        customdata=d[['count', 'churned']].values,
        hovertemplate="<b>%{x}</b><br>Churn rate: %{y:.1f}%<br>Customers: %{customdata[0]:,}<br>Churned: %{customdata[1]:,}<extra></extra>",
    ))
    l = base_layout(); l['yaxis']['title'] = "Churn Rate (%)"; l['yaxis']['range'] = [0, d['pct'].max() * 1.3]
    fig.update_layout(**l)
    st.markdown("<div class='chart-card'><div class='chart-title'>Churn Rate by Tenure Band</div><div class='chart-insight'>Customers in their first year were associated with nearly 5× higher churn than long-tenure customers — the early lifecycle is where retention is won or lost.</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with v1c2:
    d = dff.groupby('Contract').agg(
        churn_rate=('Churn', 'mean'), count=('Churn', 'count'), churned=('Churn', 'sum')
    ).reset_index().sort_values('churn_rate', ascending=False)
    d['pct'] = (d['churn_rate'] * 100).round(1)
    fig = go.Figure(go.Bar(
        x=d['Contract'], y=d['pct'],
        marker_color=[bar_color(v) for v in d['churn_rate']],
        text=[f"{v}%" for v in d['pct']], textposition='outside',
        textfont=dict(size=11, color=CHARCOAL),
        customdata=d[['count', 'churned']].values,
        hovertemplate="<b>%{x}</b><br>Churn rate: %{y:.1f}%<br>Customers: %{customdata[0]:,}<br>Churned: %{customdata[1]:,}<extra></extra>",
    ))
    l = base_layout(); l['yaxis']['title'] = "Churn Rate (%)"; l['yaxis']['range'] = [0, d['pct'].max() * 1.3]
    fig.update_layout(**l)
    st.markdown("<div class='chart-card'><div class='chart-title'>Churn Rate by Contract Type</div><div class='chart-insight'>Month-to-month customers were associated with 15× higher churn than two-year customers. Moving customers to longer contracts is the single highest-leverage retention lever.</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# VIEW 2 – CHARACTERISTICS ASSOCIATED WITH CHURN
# ════════════════════════════════════════════════════════════
st.markdown(f"<div class='section-heading'>{icon_html('eye', TEAL, 18)} View 2 &nbsp;·&nbsp; What characteristics are associated with churn?</div>", unsafe_allow_html=True)

v2c1, v2c2 = st.columns(2)

with v2c1:
    d = dff.groupby('PaymentMethod').agg(
        churn_rate=('Churn', 'mean'), count=('Churn', 'count'), churned=('Churn', 'sum')
    ).reset_index().sort_values('churn_rate', ascending=True)
    d['pct'] = (d['churn_rate'] * 100).round(1)
    d['short'] = d['PaymentMethod'].str.replace(r'\s*\(.*\)', '', regex=True).str.strip()
    fig = go.Figure(go.Bar(
        y=d['short'], x=d['pct'], orientation='h',
        marker_color=[bar_color(v) for v in d['churn_rate']],
        text=[f"{v}%" for v in d['pct']], textposition='outside',
        textfont=dict(size=11, color=CHARCOAL),
        customdata=d[['count', 'churned']].values,
        hovertemplate="<b>%{y}</b><br>Churn rate: %{x:.1f}%<br>Customers: %{customdata[0]:,}<br>Churned: %{customdata[1]:,}<extra></extra>",
    ))
    l = base_layout()
    l['xaxis'].update(title="Churn Rate (%)", range=[0, d['pct'].max() * 1.28], gridcolor=BORDER, showgrid=True)
    l['yaxis'].update(showgrid=False)
    fig.update_layout(**l)
    st.markdown("<div class='chart-card'><div class='chart-title'>Churn Rate by Payment Method</div><div class='chart-insight'>Customers who paid by electronic check were associated with nearly 3× higher churn — a proxy for lower commitment and payment friction.</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with v2c2:
    d = dff.groupby('TechSupport').agg(
        churn_rate=('Churn', 'mean'), count=('Churn', 'count'), churned=('Churn', 'sum')
    ).reset_index().sort_values('churn_rate', ascending=False)
    d['pct'] = (d['churn_rate'] * 100).round(1)
    fig = go.Figure(go.Bar(
        x=d['TechSupport'], y=d['pct'],
        marker_color=[bar_color(v) for v in d['churn_rate']],
        text=[f"{v}%" for v in d['pct']], textposition='outside',
        textfont=dict(size=11, color=CHARCOAL),
        customdata=d[['count', 'churned']].values,
        hovertemplate="<b>%{x}</b><br>Churn rate: %{y:.1f}%<br>Customers: %{customdata[0]:,}<br>Churned: %{customdata[1]:,}<extra></extra>",
    ))
    l = base_layout(); l['yaxis']['title'] = "Churn Rate (%)"; l['yaxis']['range'] = [0, d['pct'].max() * 1.3]
    fig.update_layout(**l)
    st.markdown("<div class='chart-card'><div class='chart-title'>Churn Rate by Tech Support Status</div><div class='chart-insight'>Customers who never contacted support churned at 2.7× the rate of those who did — silence is the risk signal. In production, tracking customers with zero contact in months 0–12 would be a strong early warning.</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

v2c3, v2c4 = st.columns(2)

with v2c3:
    d = dff.groupby('InternetService').agg(
        churn_rate=('Churn', 'mean'), count=('Churn', 'count'), churned=('Churn', 'sum')
    ).reset_index().sort_values('churn_rate', ascending=True)
    d['pct'] = (d['churn_rate'] * 100).round(1)
    fig = go.Figure(go.Bar(
        y=d['InternetService'], x=d['pct'], orientation='h',
        marker_color=[bar_color(v) for v in d['churn_rate']],
        text=[f"{v}%" for v in d['pct']], textposition='outside',
        textfont=dict(size=11, color=CHARCOAL),
        customdata=d[['count', 'churned']].values,
        hovertemplate="<b>%{y}</b><br>Churn rate: %{x:.1f}%<br>Customers: %{customdata[0]:,}<br>Churned: %{customdata[1]:,}<extra></extra>",
    ))
    l = base_layout()
    l['xaxis'].update(title="Churn Rate (%)", range=[0, d['pct'].max() * 1.28], gridcolor=BORDER, showgrid=True)
    l['yaxis'].update(showgrid=False)
    fig.update_layout(**l)
    st.markdown("<div class='chart-card'><div class='chart-title'>Churn Rate by Internet Service</div><div class='chart-insight'>Fibre optic customers were associated with 42% churn — double DSL — suggesting a more price-sensitive, competitive segment.</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with v2c4:
    trend = dff.groupby('tenure').agg(churn_rate=('Churn', 'mean'), count=('Churn', 'count')).reset_index()
    trend = trend[trend['count'] >= 5]
    trend['smooth'] = trend['churn_rate'].rolling(window=4, min_periods=1, center=True).mean()
    trend['pct'] = (trend['smooth'] * 100).round(1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend['tenure'], y=trend['pct'], mode='lines',
        line=dict(color=TEAL, width=2.5, shape='spline'),
        fill='tozeroy', fillcolor="rgba(10,147,150,0.08)",
        hovertemplate="Month %{x}: %{y:.1f}% churn rate<extra></extra>",
    ))
    fig.add_vrect(x0=0, x1=12, fillcolor=RED, opacity=0.05, line_width=0,
                  annotation_text="High-risk window (0–12 mo)",
                  annotation_position="top left",
                  annotation_font=dict(color=RED, size=10))
    l = base_layout(height=270)
    l['xaxis'].update(title="Tenure (months)", range=[0, 72])
    l['yaxis'].update(title="Churn Rate (%)", range=[0, trend['pct'].max() * 1.3])
    fig.update_layout(**l)
    st.markdown("<div class='chart-card'><div class='chart-title'>Churn Rate Trend Over Customer Lifetime</div><div class='chart-insight'>Churn was most concentrated in months 0–12 and declined sharply with tenure — confirming that early intervention has the highest return on retention spend.</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# VIEW 3 – WHERE TO ACT
# ════════════════════════════════════════════════════════════
st.markdown(f"<div class='section-heading'>{icon_html('target', TEAL, 18)} View 3 &nbsp;·&nbsp; Where should we act?</div>", unsafe_allow_html=True)

v3c1, v3c2 = st.columns(2)

with v3c1:
    st.markdown(f"""
    <div class="risk-callout">
      <div class="risk-label">{icon_html('warning', RED, 13)} Highest Priority Cohort</div>
      <div class="risk-number">{hr_rate:.0%}</div>
      <div class="risk-desc">
        Churn rate among <strong>{hr_count:,} customers</strong> on month-to-month
        contracts with no tech support in their first 12 months.<br><br>
        This cohort represents <strong>£{hr_mrr:,.0f}/mo</strong> in already-churned
        MRR and is the primary target for CRM retention campaigns.
      </div>
    </div>
    """, unsafe_allow_html=True)

with v3c2:
    st.markdown(f"""
    <div class="risk-callout">
      <div class="risk-label">{icon_html('signal', RED, 13)} Product Risk - Fibre Optic</div>
      <div class="risk-number">{fr_rate:.0%}</div>
      <div class="risk-desc">
        Churn rate among <strong>{fr_count:,} fibre optic customers</strong> on
        month-to-month contracts — the single largest at-risk product segment.<br><br>
        Represents <strong>£{fr_mrr:,.0f}/mo</strong> in churned MRR. Fibre customers
        are more price-sensitive and face more competitive alternatives.
      </div>
    </div>
    """, unsafe_allow_html=True)

# Priority table — full width
grouped = dff.groupby(['tenure_group', 'Contract', 'InternetService'], observed=True).agg(
    churn_rate=('Churn', 'mean'),
    customer_count=('customerID', 'count'),
    avg_risk_score=('risk_score', 'mean'),
).reset_index()
grouped['Churn Rate'] = (grouped['churn_rate'] * 100).round(1).astype(str) + '%'
grouped['Avg Risk Score'] = grouped['avg_risk_score'].round(1).astype(str) + f'/{MAX_SCORE}'
grouped['Priority'] = grouped.apply(
    lambda x: 'High'   if x['churn_rate'] >= HIGH_RISK   and x['customer_count'] > 50
    else ('Medium' if x['churn_rate'] >= MEDIUM_RISK else 'Low'), axis=1
)
grouped = grouped.sort_values('avg_risk_score', ascending=False)
grouped = grouped.rename(columns={
    'tenure_group': 'Tenure Band', 'Contract': 'Contract Type',
    'InternetService': 'Internet Service', 'customer_count': 'Customers',
})
st.dataframe(
    grouped[['Priority', 'Tenure Band', 'Contract Type', 'Internet Service', 'Customers', 'Churn Rate', 'Avg Risk Score']],
    use_container_width=True, hide_index=True
)

st.markdown(f"""
<div class="score-legend">
  <span class="score-legend-label">Risk Score</span>
  <span class="score-legend-item">{dot_html(RED, 10)} High ≥9</span>
  <span class="score-legend-item">{dot_html(AMBER, 10)} Medium 6–8</span>
  <span class="score-legend-item">{dot_html(GREEN, 10)} Low &lt;6</span>
  <span class="score-legend-item" style="color:{MUTED};font-style:italic;">
    Weighted score out of {MAX_SCORE} · Contract (×3) · Tenure 0–12mo (×3) · No tech support (×2) · Electronic check (×2) · Fibre optic (×1) · Senior (×1)
  </span>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# KEY INSIGHTS
# ════════════════════════════════════════════════════════════
st.markdown(f"<div class='section-heading'>{icon_html('lightbulb', TEAL, 18)} Key Insights</div>", unsafe_allow_html=True)

insights = [
    ("trend_down", TEAL,  "Tenure is the strongest predictor",
     "Customers in their first 12 months were associated with 47% churn — five times higher than those with 4+ years. Early lifecycle is where the battle is won or lost."),
    ("contract",   TEAL,  "Contract type creates a 15× difference",
     "Month-to-month customers were associated with 43% churn vs 2.8% for two-year customers. Moving customers to longer contracts is the single highest-leverage retention action."),
    ("payment",    AMBER, "Electronic check is a red flag",
     "Customers paying by electronic check were associated with 45% churn — nearly 3× the rate of those on automatic payments. A proxy for payment friction and lower commitment."),
    ("silent",     RED,   "Silence is the risk signal, not noise",
     "Customers who never contacted support churned at 2.7× the rate of those who did — not because they complained, but because they never engaged. Silent disengagement in months 0–12 is the warning sign to watch."),
    ("warning",    AMBER, "Risk compounds at the intersection",
     "Customers with multiple high-risk characteristics — new, unsupported, month-to-month — were associated with 61% churn. This cohort of ~1,300 is the immediate priority for retention outreach."),
    ("signal",     TEAL,  "Fibre optic is a product-level risk signal",
     "Fibre optic customers were associated with 42% churn — double DSL. On month-to-month contracts this rises to 54.6% across 2,128 customers, the largest single at-risk product segment."),
    ("revenue",    GREEN, "Revenue impact is material",
     "Monitoring churn is not just about preventing losses — it protects CLV, enables accurate revenue forecasting, and ensures retention spend is directed where it has the highest return."),
]

ic1, ic2 = st.columns(2)
for i, (ico, color, title, body) in enumerate(insights):
    with (ic1 if i % 2 == 0 else ic2):
        st.markdown(f"""
        <div class="insight-card">
          <div class="insight-icon" style="background:{'#FEF3C7' if color == AMBER else '#FEE2E2' if color == RED else '#D1FAE5' if color == GREEN else TEAL_PALE};">
            {icon_html(ico, color, 16)}
          </div>
          <div>
            <div class="insight-title">{title}</div>
            <div class="insight-body">{body}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# POTENTIAL ACTIONS
# ════════════════════════════════════════════════════════════
st.markdown(f"<div class='section-heading'>{icon_html('rocket', TEAL, 18)} Potential Actions</div>", unsafe_allow_html=True)

actions = [
    ("onboard",     TEAL,  "Improve early-lifecycle onboarding",
     "Target the 0–12 month cohort with structured onboarding comms. Reduce time-to-value before the first renewal decision point."),
    ("upgrade",     TEAL,  "Incentivise contract upgrades",
     "Offer month-to-month customers a well-timed incentive to move to 12-month contracts. The churn rate delta easily justifies meaningful acquisition cost."),
    ("outreach",    AMBER, "Proactive outreach to disengaged customers",
     "Customers who never contact support churn at nearly 3× the rate of those who do, silence is the risk signal. Proactively reach out to customers in months 0–12 who haven't engaged with support or self-serve."),
    ("investigate", AMBER, "Investigate electronic check segment",
     "Explore whether payment friction correlates with churn intent. Nudge toward automatic payment setup at onboarding."),
    ("fibre",       RED,   "Review fibre optic pricing and proposition",
     "Fibre optic customers show structurally higher churn, likely driven by competitive alternatives. Investigate whether pricing, contract incentives, or service quality is the primary driver."),
]

ac1, ac2 = st.columns(2)
for i, (ico, color, title, body) in enumerate(actions):
    with (ac1 if i % 2 == 0 else ac2):
        st.markdown(f"""
        <div class="action-card">
          <div class="action-icon" style="background:{'#FEF3C7' if color == AMBER else '#FEE2E2' if color == RED else TEAL_PALE};">
            {icon_html(ico, color, 16)}
          </div>
          <div>
            <div class="action-title">{title}</div>
            <div class="action-body">{body}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ── FOOTER ───────────────────────────────────────────────────
st.markdown(f"""
<br>
<div style="text-align:center;color:{MUTED};font-size:0.73rem;padding-bottom:1rem;">
  Kyle Laidler &nbsp;·&nbsp; Senior Technical PM Assessment &nbsp;·&nbsp; iD Mobile / Project Lantern
</div>
""", unsafe_allow_html=True)