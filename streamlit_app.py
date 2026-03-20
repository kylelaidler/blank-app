import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Churn Risk Dashboard · iD Mobile",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PALETTE ──────────────────────────────────────────────────
TEAL        = "#0A9396"
TEAL_LIGHT  = "#94D2BD"
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

# ── GLOBAL CSS ───────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{ background-color: {BG}; }}
  #MainMenu, footer, header {{ visibility: hidden; }}
  html, body, [class*="css"] {{
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color: {SLATE};
  }}
  .dash-header {{
    background: {CHARCOAL};
    padding: 1.1rem 2rem;
    border-radius: 10px;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .dash-header h1 {{ color: {WHITE}; font-size: 1.25rem; font-weight: 700; margin: 0; letter-spacing: 0.02em; }}
  .dash-header span {{ color: {TEAL}; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; }}
  .section-heading {{
    font-size: 1.1rem; font-weight: 700; color: {CHARCOAL};
    margin-bottom: 0.2rem; padding-bottom: 0.4rem; border-bottom: 2px solid {BORDER};
  }}
  .mrr-banner {{
    background: linear-gradient(135deg, {CHARCOAL} 0%, #2d3f52 100%);
    border-radius: 10px; padding: 1.3rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  }}
  .mrr-left {{ flex: 1; }}
  .mrr-eyebrow {{ font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: {TEAL}; margin-bottom: 0.3rem; }}
  .mrr-headline {{ font-size: 1.4rem; font-weight: 800; color: {WHITE}; line-height: 1.2; }}
  .mrr-sub {{ font-size: 0.82rem; color: #94A3B8; margin-top: 0.3rem; }}
  .mrr-stat {{ text-align: center; padding: 0 1.8rem; border-left: 1px solid rgba(255,255,255,0.1); }}
  .mrr-stat .stat-val {{ font-size: 1.6rem; font-weight: 800; color: {WHITE}; }}
  .mrr-stat .stat-label {{ font-size: 0.68rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 0.1rem; }}
  .chart-card {{
    background: {WHITE}; border-radius: 10px;
    padding: 1.1rem 1.1rem 0.4rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 0.5rem;
  }}
  .chart-title {{ font-size: 0.78rem; font-weight: 700; color: {MUTED}; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.1rem; }}
  .chart-insight {{ font-size: 0.82rem; color: {SLATE}; font-style: italic; margin-bottom: 0.6rem; line-height: 1.45; }}
  .risk-callout {{
    background: linear-gradient(135deg, #fff5f5 0%, {WHITE} 100%);
    border-left: 5px solid {RED}; border-radius: 10px;
    padding: 1.2rem 1.5rem; box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  }}
  .risk-label {{ font-size: 0.68rem; font-weight: 700; color: {RED}; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.25rem; }}
  .risk-number {{ font-size: 2.4rem; font-weight: 800; color: {RED}; line-height: 1; }}
  .risk-desc {{ font-size: 0.85rem; color: {SLATE}; margin-top: 0.3rem; line-height: 1.55; }}
  .insight-card {{
    background: {WHITE}; border-radius: 10px; padding: 0.9rem 1.1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06); border-left: 4px solid {TEAL};
    margin-bottom: 0.6rem; display: flex; align-items: flex-start; gap: 0.75rem;
  }}
  .insight-icon {{ font-size: 1.15rem; line-height: 1.4; flex-shrink: 0; }}
  .insight-title {{ font-weight: 700; font-size: 0.86rem; color: {CHARCOAL}; }}
  .insight-body {{ font-size: 0.8rem; color: {MUTED}; margin-top: 0.12rem; line-height: 1.5; }}
  .action-card {{
    background: {WHITE}; border-radius: 10px; padding: 0.9rem 1.1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06); border-top: 3px solid {TEAL_LIGHT}; margin-bottom: 0.6rem;
  }}
  .action-title {{ font-weight: 700; font-size: 0.86rem; color: {CHARCOAL}; }}
  .action-body {{ font-size: 0.8rem; color: {MUTED}; margin-top: 0.12rem; line-height: 1.5; }}
  .assumption-row {{
    display: flex; gap: 0.7rem; align-items: flex-start;
    padding: 0.5rem 0; border-bottom: 1px solid {BORDER};
  }}
  .assumption-row:last-child {{ border-bottom: none; }}
  .assume-badge {{
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.07em;
    padding: 0.13rem 0.4rem; border-radius: 4px; flex-shrink: 0; margin-top: 0.06rem;
  }}
  .badge-assume {{ background: {AMBER_PALE}; color: #92400E; }}
  .badge-missing {{ background: {RED_PALE}; color: #991B1B; }}
  .badge-valid {{ background: #D1FAE5; color: #065F46; }}
  .assume-text {{ font-size: 0.8rem; color: {SLATE}; line-height: 1.5; }}
  .upload-box {{
    background: {WHITE}; border: 2px dashed {BORDER}; border-radius: 12px;
    padding: 2.5rem; text-align: center; margin: 2rem auto; max-width: 500px;
  }}
  .upload-box h3 {{ color: {CHARCOAL}; font-size: 1rem; margin-bottom: 0.3rem; }}
  .upload-box p {{ color: {MUTED}; font-size: 0.83rem; }}
  .divider {{ border: none; border-top: 1px solid {BORDER}; margin: 1.5rem 0; }}
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


# ── HEADER ───────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
  <h1>Churn-a-nator · Prioritisation Dashboard</h1>
  <span>iD Mobile &nbsp;·&nbsp; Project Lantern</span>
</div>
""", unsafe_allow_html=True)

# ── UPLOAD ───────────────────────────────────────────────────
upload_slot = st.empty()
with upload_slot.container():
    st.markdown('<div class="upload-box"><h3>Upload your churn dataset</h3><p>CSV file · IBM Telco Churn format</p></div>', unsafe_allow_html=True)
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

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='padding:0.5rem 0 0.8rem'><div style='font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:{TEAL};margin-bottom:0.25rem;'>iD Mobile</div><div style='font-size:1rem;font-weight:700;color:white;'>Churn Dashboard</div></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.68rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:{TEAL};margin-bottom:0.5rem;'>Filters</div>", unsafe_allow_html=True)
    contract_filter = st.selectbox("Contract Type",   ["All"] + sorted(df['Contract'].unique().tolist()))
    tech_filter     = st.selectbox("Tech Support",    ["All"] + sorted(df['TechSupport'].unique().tolist()))
    payment_filter  = st.selectbox("Payment Method",  ["All"] + sorted(df['PaymentMethod'].unique().tolist()))
    tenure_range    = st.slider("Tenure (months)", 0, 72, (0, 72))
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.72rem;color:#94A3B8;line-height:1.6;'>High risk threshold: >{HIGH_RISK:.0%} churn rate.<br>Filters apply across all views.</div>", unsafe_allow_html=True)

# ── APPLY FILTERS ────────────────────────────────────────────
dff = df.copy()
if contract_filter != "All": dff = dff[dff['Contract']      == contract_filter]
if tech_filter     != "All": dff = dff[dff['TechSupport']   == tech_filter]
if payment_filter  != "All": dff = dff[dff['PaymentMethod'] == payment_filter]
dff = dff[(dff['tenure'] >= tenure_range[0]) & (dff['tenure'] <= tenure_range[1])]

# ── KPIs ─────────────────────────────────────────────────────
churn_rate     = dff['Churn'].mean()
churned_count  = int(dff['Churn'].sum())
total          = len(dff)
avg_charge     = dff['MonthlyCharges'].mean()
mrr_at_risk    = dff[dff['Churn'] == 1]['MonthlyCharges'].sum()

high_risk = dff[(dff['Contract'] == 'Month-to-month') & (dff['TechSupport'] == 'No') & (dff['tenure'] <= 12)]
hr_rate   = high_risk['Churn'].mean() if len(high_risk) else 0
hr_count  = len(high_risk)
hr_mrr    = high_risk[high_risk['Churn'] == 1]['MonthlyCharges'].sum()

# ── MRR BANNER ───────────────────────────────────────────────
st.markdown(f"""
<div class="mrr-banner">
  <div class="mrr-left">
    <div class="mrr-eyebrow">⚠ Revenue at Risk · Current Filtered View</div>
    <div class="mrr-headline">£{mrr_at_risk:,.0f} in monthly recurring revenue has already churned</div>
    <div class="mrr-sub">
      {churned_count:,} churned customers at an average of £{avg_charge:.0f}/mo.
      High-risk cohort (month-to-month · no support · 0–12 mo) accounts for £{hr_mrr:,.0f} of this.
    </div>
  </div>
  <div class="mrr-stat"><div class="stat-val">{churn_rate:.1%}</div><div class="stat-label">Churn Rate</div></div>
  <div class="mrr-stat"><div class="stat-val">{churned_count:,}</div><div class="stat-label">Churned</div></div>
  <div class="mrr-stat"><div class="stat-val">{total:,}</div><div class="stat-label">In View</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# VIEW 1 – WHERE IS CHURN CONCENTRATED
# ════════════════════════════════════════════════════════════
st.markdown("<div class='section-heading'>View 1 &nbsp;·&nbsp; Where is churn concentrated?</div>", unsafe_allow_html=True)

v1c1, v1c2 = st.columns(2)

with v1c1:
    d = dff.groupby('tenure_group', observed=True).agg(
        churn_rate=('Churn','mean'), count=('Churn','count'), churned=('Churn','sum')
    ).reset_index()
    d['pct'] = (d['churn_rate'] * 100).round(1)
    fig = go.Figure(go.Bar(
        x=d['tenure_group'].astype(str), y=d['pct'],
        marker_color=[bar_color(v) for v in d['churn_rate']],
        text=[f"{v}%" for v in d['pct']], textposition='outside',
        textfont=dict(size=11, color=CHARCOAL),
        customdata=d[['count','churned']].values,
        hovertemplate="<b>%{x}</b><br>Churn rate: %{y:.1f}%<br>Customers: %{customdata[0]:,}<br>Churned: %{customdata[1]:,}<extra></extra>",
    ))
    l = base_layout(); l['yaxis']['title'] = "Churn Rate (%)"; l['yaxis']['range'] = [0, d['pct'].max() * 1.3]
    fig.update_layout(**l)
    st.markdown("<div class='chart-card'><div class='chart-title'>Churn Rate by Tenure Band</div><div class='chart-insight'>Customers in their first year churn at nearly 5× the rate of long-tenure customers — the early lifecycle is where retention is won or lost.</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with v1c2:
    d = dff.groupby('Contract').agg(
        churn_rate=('Churn','mean'), count=('Churn','count'), churned=('Churn','sum')
    ).reset_index().sort_values('churn_rate', ascending=False)
    d['pct'] = (d['churn_rate'] * 100).round(1)
    fig = go.Figure(go.Bar(
        x=d['Contract'], y=d['pct'],
        marker_color=[bar_color(v) for v in d['churn_rate']],
        text=[f"{v}%" for v in d['pct']], textposition='outside',
        textfont=dict(size=11, color=CHARCOAL),
        customdata=d[['count','churned']].values,
        hovertemplate="<b>%{x}</b><br>Churn rate: %{y:.1f}%<br>Customers: %{customdata[0]:,}<br>Churned: %{customdata[1]:,}<extra></extra>",
    ))
    l = base_layout(); l['yaxis']['title'] = "Churn Rate (%)"; l['yaxis']['range'] = [0, d['pct'].max() * 1.3]
    fig.update_layout(**l)
    st.markdown("<div class='chart-card'><div class='chart-title'>Churn Rate by Contract Type</div><div class='chart-insight'>Month-to-month customers churn at 15× the rate of two-year customers. Moving customers to longer contracts is the single highest-leverage retention lever.</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# VIEW 2 – SIGNALS & TREND
# ════════════════════════════════════════════════════════════
st.markdown("<div class='section-heading'>View 2 &nbsp;·&nbsp; What signals indicate churn risk?</div>", unsafe_allow_html=True)

v2c1, v2c2 = st.columns(2)

with v2c1:
    d = dff.groupby('PaymentMethod').agg(
        churn_rate=('Churn','mean'), count=('Churn','count'), churned=('Churn','sum')
    ).reset_index().sort_values('churn_rate', ascending=True)
    d['pct'] = (d['churn_rate'] * 100).round(1)
    d['short'] = d['PaymentMethod'].str.replace(r'\s*\(.*\)', '', regex=True).str.strip()
    fig = go.Figure(go.Bar(
        y=d['short'], x=d['pct'], orientation='h',
        marker_color=[bar_color(v) for v in d['churn_rate']],
        text=[f"{v}%" for v in d['pct']], textposition='outside',
        textfont=dict(size=11, color=CHARCOAL),
        customdata=d[['count','churned']].values,
        hovertemplate="<b>%{y}</b><br>Churn rate: %{x:.1f}%<br>Customers: %{customdata[0]:,}<br>Churned: %{customdata[1]:,}<extra></extra>",
    ))
    l = base_layout()
    l['xaxis'].update(title="Churn Rate (%)", range=[0, d['pct'].max() * 1.28], gridcolor=BORDER, showgrid=True)
    l['yaxis'].update(showgrid=False)
    fig.update_layout(**l)
    st.markdown("<div class='chart-card'><div class='chart-title'>Churn Rate by Payment Method</div><div class='chart-insight'>Electronic check customers churn at nearly 3× the rate of those on automatic payments — a proxy for lower commitment and payment friction.</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with v2c2:
    d = dff.groupby('TechSupport').agg(
        churn_rate=('Churn','mean'), count=('Churn','count'), churned=('Churn','sum')
    ).reset_index().sort_values('churn_rate', ascending=False)
    d['pct'] = (d['churn_rate'] * 100).round(1)
    fig = go.Figure(go.Bar(
        x=d['TechSupport'], y=d['pct'],
        marker_color=[bar_color(v) for v in d['churn_rate']],
        text=[f"{v}%" for v in d['pct']], textposition='outside',
        textfont=dict(size=11, color=CHARCOAL),
        customdata=d[['count','churned']].values,
        hovertemplate="<b>%{x}</b><br>Churn rate: %{y:.1f}%<br>Customers: %{customdata[0]:,}<br>Churned: %{customdata[1]:,}<extra></extra>",
    ))
    l = base_layout(); l['yaxis']['title'] = "Churn Rate (%)"; l['yaxis']['range'] = [0, d['pct'].max() * 1.3]
    fig.update_layout(**l)
    st.markdown("<div class='chart-card'><div class='chart-title'>Churn Rate by Tech Support Status</div><div class='chart-insight'>Customers without tech support churn at 2.7× the rate of those with it — contact frequency is an early warning signal, not just a cost driver.</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# Trend line
trend = dff.groupby('tenure').agg(churn_rate=('Churn','mean'), count=('Churn','count')).reset_index()
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
l = base_layout(height=230)
l['xaxis'].update(title="Tenure (months)", range=[0, 72])
l['yaxis'].update(title="Churn Rate (%)", range=[0, trend['pct'].max() * 1.3])
fig.update_layout(**l)

st.markdown("<div class='chart-card'><div class='chart-title'>Churn Rate Trend Over Customer Lifetime</div><div class='chart-insight'>Churn risk peaks in months 0–12 and declines sharply as tenure grows — confirming that early intervention has the highest return on retention spend.</div>", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# VIEW 3 – WHERE TO ACT
# ════════════════════════════════════════════════════════════
st.markdown("<div class='section-heading'>View 3 &nbsp;·&nbsp; Where should we act first?</div>", unsafe_allow_html=True)

v3c1, v3c2 = st.columns([1, 2])

with v3c1:
    st.markdown(f"""
    <div class="risk-callout">
      <div class="risk-label">⚠ Highest Priority Cohort</div>
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
    grouped = dff.groupby(['tenure_group', 'Contract'], observed=True).agg(
        churn_rate=('Churn', 'mean'),
        customer_count=('customerID', 'count'),
    ).reset_index()
    grouped['Churn Rate'] = (grouped['churn_rate'] * 100).round(1).astype(str) + '%'
    grouped['Priority'] = grouped.apply(
        lambda x: '🔴 High'   if x['churn_rate'] >= HIGH_RISK   and x['customer_count'] > 100
        else ('🟡 Medium' if x['churn_rate'] >= MEDIUM_RISK else '🟢 Low'), axis=1
    )
    grouped = grouped.sort_values('churn_rate', ascending=False)
    grouped = grouped.rename(columns={'tenure_group': 'Tenure Band', 'Contract': 'Contract Type', 'customer_count': 'Customers'})
    st.dataframe(grouped[['Priority', 'Tenure Band', 'Contract Type', 'Customers', 'Churn Rate']],
                 use_container_width=True, hide_index=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# INSIGHTS
# ════════════════════════════════════════════════════════════
st.markdown("<div class='section-heading'>Key Insights</div>", unsafe_allow_html=True)

insights = [
    ("📉", "Tenure is the strongest predictor",       "Customers in their first 12 months churn at 47% — five times higher than those with 4+ years. Early lifecycle is where the battle is won or lost."),
    ("📋", "Contract type creates a 15× difference",  "Month-to-month customers churn at 43%. Two-year customers at 2.8%. Moving customers to longer contracts is the single highest-leverage retention action."),
    ("💳", "Electronic check is a red flag",          "Customers paying by electronic check churn at 45% — nearly 3× the rate of those on automatic payments. A strong proxy for payment friction and low commitment."),
    ("🛠️", "No tech support = 2.7× churn risk",      "Customers without tech support churn at 42% vs 15% with it. Contact centre contacts are a leading signal, not just a cost driver."),
    ("⚠️", "Risk compounds at the intersection",      "New, unsupported, month-to-month customers hit 61% churn. This cohort of ~1,300 should be the immediate focus for proactive retention outreach."),
]

ic1, ic2 = st.columns(2)
for i, (icon, title, body) in enumerate(insights):
    with (ic1 if i % 2 == 0 else ic2):
        st.markdown(f'<div class="insight-card"><div class="insight-icon">{icon}</div><div><div class="insight-title">{title}</div><div class="insight-body">{body}</div></div></div>', unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ACTIONS
# ════════════════════════════════════════════════════════════
st.markdown("<div class='section-heading'>Potential Actions</div>", unsafe_allow_html=True)

actions = [
    ("Improve early-lifecycle onboarding",    "Target the 0–12 month cohort with structured onboarding comms. Reduce time-to-value before the first renewal decision point."),
    ("Incentivise contract upgrades",         "Offer month-to-month customers a well-timed incentive to move to 12-month contracts. The churn delta easily justifies meaningful acquisition cost."),
    ("Proactive tech support outreach",       "Flag customers with multiple contacts and no resolution. Intervene before they disengage entirely."),
    ("Investigate electronic check segment",  "Explore whether payment friction correlates with churn intent. Nudge toward automatic payment setup at onboarding."),
]

ac1, ac2 = st.columns(2)
for i, (title, body) in enumerate(actions):
    with (ac1 if i % 2 == 0 else ac2):
        st.markdown(f'<div class="action-card"><div class="action-title">{title}</div><div class="action-body">{body}</div></div>', unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ASSUMPTIONS
# ════════════════════════════════════════════════════════════
with st.expander("📋  Data assumptions & what I'd validate with iD Mobile"):
    for flag, cls, text in [
        ("ASSUME",  "badge-assume",   "'TechSupport = No' used as proxy for contact frequency. Validate: match against CRM contact logs by customer ID."),
        ("ASSUME",  "badge-assume",   "Tenure bands assumed business-meaningful. Validate with CRM: do retention campaigns already segment by these cohorts?"),
        ("ASSUME",  "badge-assume",   "Electronic check treated as proxy for payment risk. Validate against direct debit failure rates in iD billing data."),
        ("MISSING", "badge-missing",  "Actual contact volume not in dataset. Production version would link to Contact Centre data for true contact frequency per customer."),
        ("MISSING", "badge-missing",  "No payment failure data. Direct debit failure signals from iD billing would likely be a strong additional early warning indicator."),
        ("MISSING", "badge-missing",  "No product usage data (data usage, call minutes). Declining usage before churn is a key signal this dataset cannot capture."),
        ("VALID",   "badge-valid",    "Churn flag, contract type, and tenure are structurally equivalent to iD Mobile's subscription data model. Findings are directionally accurate."),
        ("VALID",   "badge-valid",    "Overall churn rate of 26.5% is higher than typical UK MVNO benchmarks — treat as illustrative of pattern, not absolute rate."),
    ]:
        st.markdown(f'<div class="assumption-row"><span class="assume-badge {cls}">{flag}</span><span class="assume-text">{text}</span></div>', unsafe_allow_html=True)

# ── FOOTER ───────────────────────────────────────────────────
st.markdown(f'<br><div style="text-align:center;color:{MUTED};font-size:0.73rem;padding-bottom:1rem;">Kyle Laidler &nbsp;·&nbsp; Senior Technical PM Assessment &nbsp;·&nbsp; iD Mobile / Project Lantern</div>', unsafe_allow_html=True)