import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 18px; }
</style>
""", unsafe_allow_html=True)
st.title("CBAM Cost Comparison Model (BF vs EAF)")

# =========================
# Sidebar inputs
# =========================
st.sidebar.header("Input parameters")

# Year slider — drives CF and carbon prices automatically
st.sidebar.subheader("Year (CBAM trajectory)")
year = st.sidebar.slider("Year", 2026, 2034, 2034)

# Table 4.1: official CF schedule
cf_schedule = {
    2026: 0.975, 2027: 0.950, 2028: 0.900, 2029: 0.775, 2030: 0.515,
    2031: 0.390, 2032: 0.265, 2033: 0.140, 2034: 0.000,
}
cf = cf_schedule[year]

# Table 4.2 / Fig 4.4: carbon price trajectory (anchor midpoints; 2034 = 150/32 reference case)
_ay = [2026, 2028, 2030, 2032, 2034]
price_eu = float(np.interp(year, _ay, [80,  100, 120, 140, 150]))
price_cn = float(np.interp(year, _ay, [12.5, 22.5, 29,  31,  32]))

st.sidebar.caption(
    f"CF = {cf:.3f} (Table 4.1)  \n"
    f"EU ETS ≈ {price_eu:.0f} €/tCO₂ · China ETS ≈ {price_cn:.1f} €/tCO₂  \n"
    f"(Table 4.2 / Fig. 4.4, anchored to 150/32 at 2034)"
)

# Technology parameters (Table 4.3)
st.sidebar.subheader("Production technology")
s1_bf  = st.sidebar.slider("BF-BOF Scope 1 intensity (tCO2/t steel)", 2.1, 2.5, 2.30)
s1_eaf = st.sidebar.slider("EAF Scope 1 intensity (tCO2/t steel)", 0.15, 0.30, 0.22)
e_bf   = st.sidebar.slider("BF-BOF electricity consumption (kWh/t steel)", 30, 100, 50)
e_eaf  = st.sidebar.slider("EAF electricity consumption (kWh/t steel)", 300, 600, 575)

# Emission factors
st.sidebar.subheader("Electricity emission factors")
ef_grid  = st.sidebar.slider("Grid emission factor (tCO2/MWh)", 0.4, 0.8, 0.55)
ef_renew = st.sidebar.slider("Renewable emission factor (tCO2/MWh)", 0.0, 0.05, 0.02)

# CBAM parameters
st.sidebar.subheader("CBAM parameters")
benchmark = st.sidebar.slider("Benchmark (tCO2/t)", 0.0, 2.5, 1.328)

# Electricity prices
st.sidebar.subheader("Electricity prices")
price_grid  = st.sidebar.slider("Grid price (€/MWh)", 40, 120, 75)
lcoe_renew  = st.sidebar.slider("Renewable LCOE (€/MWh generated)", 20, 45, 30)
extra_cost  = st.sidebar.slider("Additional system cost (€/MWh self-consumed)", 35, 65, 42)

# Renewable assumptions
st.sidebar.subheader("Renewable electricity assumptions")
alpha      = st.sidebar.slider("Self-consumption ratio", 0.6, 1.0, 0.7)
price_sell = st.sidebar.slider("Grid sell-back price (€/MWh exported)", 0, 15, 5)

# Material costs
st.sidebar.subheader("Material costs")
iron_ore_cost = st.sidebar.slider("Iron ore cost (€/t steel)", 90, 130, 108)
coal_cost     = st.sidebar.slider("Coal cost (€/t steel)", 90, 140, 105)
scrap_cost    = st.sidebar.slider("Scrap cost (€/t steel)", 280, 320, 295)

# =========================
# Calculations
# =========================

# Emissions
scope2_bf       = e_bf  / 1000 * ef_grid
scope2_eaf_grid = e_eaf / 1000 * ef_grid
scope2_eaf_renew= e_eaf / 1000 * ef_renew
ee_bf           = s1_bf  + scope2_bf
ee_eaf_grid     = s1_eaf + scope2_eaf_grid
ee_eaf_renew    = s1_eaf + scope2_eaf_renew

# CBAM (Eq. 4.8) — current (Scope 1) and extended (Scope 1+2)
dp = price_eu - price_cn
cbam_bf_cur      = max((s1_bf   - benchmark * cf) * dp, 0)
cbam_eaf_grid_cur= max((s1_eaf  - benchmark * cf) * dp, 0)
cbam_eaf_renew_cur=max((s1_eaf  - benchmark * cf) * dp, 0)

cbam_bf_ext      = max((ee_bf        - benchmark * cf) * dp, 0)
cbam_eaf_grid_ext= max((ee_eaf_grid  - benchmark * cf) * dp, 0)
cbam_eaf_renew_ext=max((ee_eaf_renew - benchmark * cf) * dp, 0)

# Electricity cost (Eq. 4.7)
price_renew_eff = max(
    lcoe_renew / alpha + extra_cost - (min(1 - alpha, 0.2) / alpha) * price_sell, 0
)
elec_bf        = e_bf  / 1000 * price_grid
elec_eaf_grid  = e_eaf / 1000 * price_grid
elec_eaf_renew = e_eaf / 1000 * price_renew_eff

# Production cost (Eq. 4.4-4.6)
prod_bf        = elec_bf       + coal_cost + iron_ore_cost
prod_eaf_grid  = elec_eaf_grid + scrap_cost
prod_eaf_renew = elec_eaf_renew+ scrap_cost

# Total cost (Eq. 4.3)
total_bf_cur        = prod_bf        + cbam_bf_cur
total_bf_ext        = prod_bf        + cbam_bf_ext
total_eaf_grid_cur  = prod_eaf_grid  + cbam_eaf_grid_cur
total_eaf_grid_ext  = prod_eaf_grid  + cbam_eaf_grid_ext
total_eaf_renew_cur = prod_eaf_renew + cbam_eaf_renew_cur
total_eaf_renew_ext = prod_eaf_renew + cbam_eaf_renew_ext

# =========================
# Year banner
# =========================
st.info(
    f"**Year: {year}** — CF = {cf:.3f} (Table 4.1) · "
    f"EU ETS ≈ {price_eu:.0f} €/tCO₂ · China ETS ≈ {price_cn:.1f} €/tCO₂"
)

# =========================
# Metric cards
# =========================
st.subheader("Technology and electricity scenarios")
col1, col2, col3 = st.columns(3)

with col1:
    st.write("### BF-BOF (Grid)")
    st.metric("Scope 1", f"{s1_bf:.2f} tCO₂/t")
    st.metric("Scope 2", f"{scope2_bf:.2f} tCO₂/t")
    st.metric("Embedded emissions", f"{ee_bf:.2f} tCO₂/t")
    st.metric("Production cost", f"{prod_bf:.1f} €/t")
    st.metric("CBAM (current)", f"{cbam_bf_cur:.1f} €/t")
    st.metric("CBAM (extended)", f"{cbam_bf_ext:.1f} €/t")
    st.metric("Total cost (current)", f"{total_bf_cur:.1f} €/t")
    st.metric("Total cost (extended)", f"{total_bf_ext:.1f} €/t")

with col2:
    st.write("### EAF (Grid)")
    st.metric("Scope 1", f"{s1_eaf:.2f} tCO₂/t")
    st.metric("Scope 2", f"{scope2_eaf_grid:.2f} tCO₂/t")
    st.metric("Embedded emissions", f"{ee_eaf_grid:.2f} tCO₂/t")
    st.metric("Production cost", f"{prod_eaf_grid:.1f} €/t")
    st.metric("CBAM (current)", f"{cbam_eaf_grid_cur:.1f} €/t")
    st.metric("CBAM (extended)", f"{cbam_eaf_grid_ext:.1f} €/t")
    st.metric("Total cost (current)", f"{total_eaf_grid_cur:.1f} €/t")
    st.metric("Total cost (extended)", f"{total_eaf_grid_ext:.1f} €/t")

with col3:
    st.write("### EAF (Renewable)")
    st.metric("Scope 1", f"{s1_eaf:.2f} tCO₂/t")
    st.metric("Scope 2", f"{scope2_eaf_renew:.2f} tCO₂/t")
    st.metric("Embedded emissions", f"{ee_eaf_renew:.2f} tCO₂/t")
    st.metric("Production cost", f"{prod_eaf_renew:.1f} €/t")
    st.metric("CBAM (current)", f"{cbam_eaf_renew_cur:.1f} €/t")
    st.metric("CBAM (extended)", f"{cbam_eaf_renew_ext:.1f} €/t")
    st.metric("Total cost (current)", f"{total_eaf_renew_cur:.1f} €/t")
    st.metric("Total cost (extended)", f"{total_eaf_renew_ext:.1f} €/t")

# =========================
# =========================
# Colour palette — matches Figure 5.2 exactly
#   BF-BOF   : dark blue  / light blue
#   EAF grid : dark red   / light red
#   EAF renew: dark green / light green
# =========================
C_BF_DARK   = "#2171b5"
C_BF_LIGHT  = "#9ecae1"
C_GRID_DARK = "#cb4b19"
C_GRID_LIGHT= "#f4a582"
C_RENEW_DARK = "#238b45"
C_RENEW_LIGHT= "#a1d99b"

SCENARIOS   = ["BF-BOF (Grid)", "EAF (Grid)", "EAF (Renewable)"]
DARK_COLORS = [C_BF_DARK,  C_GRID_DARK,  C_RENEW_DARK]
LIGHT_COLORS= [C_BF_LIGHT, C_GRID_LIGHT, C_RENEW_LIGHT]

def make_chart(title, current_vals, extended_vals=None, ylabel="€/t steel"):
    """Two-trace grouped bar (current = dark, extended = light) or single-trace."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Current framework",
        x=SCENARIOS,
        y=[max(v, 0) for v in current_vals],
        marker_color=DARK_COLORS,
        marker_line_width=0,
    ))
    if extended_vals is not None:
        fig.add_trace(go.Bar(
            name="Extended framework",
            x=SCENARIOS,
            y=[max(v, 0) for v in extended_vals],
            marker_color=LIGHT_COLORS,
            marker_line_color=DARK_COLORS,
            marker_line_width=1.2,
        ))
    fig.update_layout(
        title=title,
        barmode="group",
        yaxis_title=ylabel,
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=40),
    )
    fig.update_yaxes(rangemode="tozero", showgrid=True, gridcolor="#eeeeee")
    fig.update_xaxes(showgrid=False)
    return fig

# =========================
# Plot 1: CBAM — current framework
# =========================
st.subheader("CBAM (Current framework)")
fig1 = make_chart(
    f"CBAM cost — current framework ({year})",
    current_vals=[cbam_bf_cur, cbam_eaf_grid_cur, cbam_eaf_renew_cur],
)
st.plotly_chart(fig1, use_container_width=True)

# =========================
# Plot 2: CBAM — current vs extended
# =========================
st.subheader("CBAM: Current vs Extended framework")
fig2 = make_chart(
    f"CBAM cost — current vs extended framework ({year})",
    current_vals= [cbam_bf_cur,  cbam_eaf_grid_cur,  cbam_eaf_renew_cur],
    extended_vals=[cbam_bf_ext,  cbam_eaf_grid_ext,  cbam_eaf_renew_ext],
)
st.plotly_chart(fig2, use_container_width=True)

# =========================
# Plot 3: Electricity cost
# =========================
st.subheader("Electricity cost")
fig3 = make_chart(
    f"Electricity cost component ({year})",
    current_vals=[elec_bf, elec_eaf_grid, elec_eaf_renew],
)
st.plotly_chart(fig3, use_container_width=True)

# =========================
# Plot 4: Total cost — current vs extended
# =========================
st.subheader("Total Cost (production + CBAM)")
fig4 = make_chart(
    f"Total cost — current vs extended framework ({year})",
    current_vals= [total_bf_cur,  total_eaf_grid_cur,  total_eaf_renew_cur],
    extended_vals=[total_bf_ext,  total_eaf_grid_ext,  total_eaf_renew_ext],
)
st.plotly_chart(fig4, use_container_width=True)


# =========================
# Key insights
# =========================
st.subheader("Key insights")

diff_cbam = cbam_eaf_grid_ext - cbam_eaf_renew_ext
st.write(
    f"Switching from grid to renewable electricity reduces **extended CBAM** by "
    f"**{diff_cbam:.1f} €/t steel** in {year}."
)

savings_elec = elec_eaf_grid - elec_eaf_renew
if savings_elec > 0:
    st.write(
        f"Renewable electricity saves **{savings_elec:.1f} €/t steel** on the electricity "
        f"component vs grid (EAF route)."
    )
else:
    st.write(
        f"Renewable electricity costs **{-savings_elec:.1f} €/t steel more** than grid "
        f"electricity on the electricity component (EAF route)."
    )

diff_total = total_eaf_grid_ext - total_eaf_renew_ext
st.write(
    f"Under the **extended framework**, EAF (Renewable) total cost is "
    f"**{abs(diff_total):.1f} €/t {'lower' if diff_total > 0 else 'higher'}** than EAF (Grid) in {year}."
)

diff_vs_bf = total_bf_ext - total_eaf_renew_ext
st.write(
    f"BF-BOF total cost is **{abs(diff_vs_bf):.1f} €/t "
    f"{'higher' if diff_vs_bf > 0 else 'lower'}** than EAF (Renewable) "
    f"under the extended framework in {year}."
)
