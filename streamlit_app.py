import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)
st.title("CBAM Cost Comparison Model (BF vs EAF)")

# =========================
# Sidebar inputs
# =========================
st.sidebar.header("Input parameters")

# Technology-specific parameters (Table 4.3 ranges)
st.sidebar.subheader("Production technology")
s1_bf = st.sidebar.slider("BF-BOF Scope 1 intensity (tCO2/t steel)", 2.1, 2.5, 2.30)
s1_eaf = st.sidebar.slider("EAF Scope 1 intensity (tCO2/t steel)", 0.15, 0.30, 0.22)
e_bf = st.sidebar.slider("BF-BOF electricity consumption (kWh/t steel)", 30, 100, 50)

e_eaf = st.sidebar.slider(
    "EAF electricity consumption (kWh/t steel)",
    300, 600, 575
)

# Electricity sourcing
st.sidebar.subheader("Electricity emission factors")
ef_grid = st.sidebar.slider("Grid emission factor (tCO2/MWh)", 0.4, 0.8, 0.8)
ef_renew = st.sidebar.slider("Renewable emission factor (tCO2/MWh)", 0.0, 0.05, 0.02)

# Year (drives CBAM factor and carbon price trajectory)
st.sidebar.subheader("Year (CBAM trajectory)")
year = st.sidebar.slider("Year", 2026, 2034, 2034)

# Table 4.1: official CBAM phase-out factor (CF) schedule, 2026-2034
cf_schedule = {
    2026: 0.975, 2027: 0.950, 2028: 0.900, 2029: 0.775, 2030: 0.515,
    2031: 0.390, 2032: 0.265, 2033: 0.140, 2034: 0.000,
}
cf = cf_schedule[year]

# Table 4.2 / Figure 4.4: carbon price trajectory. Anchor values are the midpoint
# of the stated ranges at each anchor year, linearly interpolated in between.
price_anchor_years = [2026, 2028, 2030, 2032, 2034]
price_eu_anchors = [80, 100, 120, 140, 150]      # midpoints of 75-85, 80-120, 90-150, 105-175; 2034 set to the
price_cn_anchors = [12.5, 22.5, 29, 31, 32]      # central value (150/32) used in Table 4.3 and the Sec. 5.2.1 reference calc

price_eu = float(np.interp(year, price_anchor_years, price_eu_anchors))
price_cn = float(np.interp(year, price_anchor_years, price_cn_anchors))

st.sidebar.caption(
    f"CF = {cf:.3f} (Table 4.1)  \n"
    f"EU ETS \u2248 {price_eu:.0f} \u20ac/tCO\u2082, China ETS \u2248 {price_cn:.1f} \u20ac/tCO\u2082 "
    f"(Table 4.2 / Fig. 4.4 trajectory)"
)

# CBAM parameters
st.sidebar.subheader("CBAM parameters")
benchmark = st.sidebar.slider("Benchmark (tCO2/t)", 0.0, 2.5, 1.328)

# Electricity price
st.sidebar.subheader("Electricity price")
price_grid = st.sidebar.slider("Grid price (€/MWh)", 40, 120, 70)
lcoe_renew = st.sidebar.slider("Renewable LCOE (€/MWh generated)", 25, 35, 30)
extra_cost = st.sidebar.slider("Additional system cost (€/MWh self-consumed)", 35, 65, 42)
price_renew = lcoe_renew + extra_cost

# Renewable assumptions
st.sidebar.subheader("Renewable electricity assumptions")
alpha = st.sidebar.slider("Self-consumption ratio", 0.6, 1.0, 0.7)
price_sell = st.sidebar.slider("Grid sell-back price (€/MWh exported)", 0, 15, 5)

# Material costs (Table 4.3)
st.sidebar.subheader("Material costs")
iron_ore_cost = st.sidebar.slider("Iron ore cost (€/t steel)", 90, 130, 108)
coal_cost = st.sidebar.slider("Coal cost (€/t steel)", 90, 140, 105)
scrap_cost = st.sidebar.slider("Scrap cost (€/t steel)", 280, 320, 295)

# =========================
# Emissions scenario calculations
# =========================

# --- BF-BOF (baseline) ---
scope1_bf = s1_bf
scope2_bf = e_bf / 1000 * ef_grid
ee_bf = scope1_bf + scope2_bf

# --- EAF Grid ---
scope1_eaf = s1_eaf
scope2_eaf_grid = e_eaf / 1000 * ef_grid
ee_eaf_grid = scope1_eaf + scope2_eaf_grid

# --- EAF Renewable ---
scope2_eaf_renew = e_eaf / 1000 * ef_renew
ee_eaf_renew = scope1_eaf + scope2_eaf_renew

# =========================
# CBAM calculations (Eq. 4.8-style: chargeable emissions x carbon price differential)
# =========================

# Current CBAM framework (Scope 1 only, all routes)
cbam_bf_current = (scope1_bf - benchmark * cf) * (price_eu - price_cn)
cbam_eaf_grid_current = (scope1_eaf - benchmark * cf) * (price_eu - price_cn)
cbam_eaf_renew_current = cbam_eaf_grid_current

# Extended CBAM framework (Scope 1 + Scope 2, all routes)
cbam_bf_extended = (ee_bf - benchmark * cf) * (price_eu - price_cn)
cbam_eaf_grid_extended = (ee_eaf_grid - benchmark * cf) * (price_eu - price_cn)
cbam_eaf_renew_extended = (ee_eaf_renew - benchmark * cf) * (price_eu - price_cn)

# =========================
# Electricity cost (Eq. 4.7)
# =========================
# P_eff_renew = P_renew/alpha + C_sys - [min(1-alpha,0.2)/alpha] * P_sell
# C_sys (extra_cost) is already expressed per MWh self-consumed, so it is added
# directly and must NOT be divided by alpha (unlike the LCOE and sell-back terms).
price_renew_effective = max(
    lcoe_renew / alpha + extra_cost - (min(1 - alpha, 0.2) / alpha) * price_sell,
    0
)

elec_cost_bf = e_bf / 1000 * price_grid
elec_cost_eaf_grid = e_eaf / 1000 * price_grid
elec_cost_eaf_renew = e_eaf / 1000 * price_renew_effective

# =========================
# Production cost (Eq. 4.4 - 4.6) and Total cost (Eq. 4.3)
# =========================

prod_cost_bf = elec_cost_bf + coal_cost + iron_ore_cost                 # Eq. 4.4
prod_cost_eaf_grid = elec_cost_eaf_grid + scrap_cost                    # Eq. 4.5
prod_cost_eaf_renew = elec_cost_eaf_renew + scrap_cost                  # Eq. 4.6

# Total Cost = C_prod + C_CBAM (Eq. 4.3), under each CBAM framework
total_bf_current = prod_cost_bf + cbam_bf_current
total_bf_extended = prod_cost_bf + cbam_bf_extended

total_eaf_grid_current = prod_cost_eaf_grid + cbam_eaf_grid_current
total_eaf_grid_extended = prod_cost_eaf_grid + cbam_eaf_grid_extended

total_eaf_renew_current = prod_cost_eaf_renew + cbam_eaf_renew_current
total_eaf_renew_extended = prod_cost_eaf_renew + cbam_eaf_renew_extended

# =========================
st.info(
    f"**Year: {year}** \u2014 CBAM factor CF = {cf:.3f} (Table 4.1) \u00b7 "
    f"EU ETS \u2248 {price_eu:.0f} \u20ac/tCO\u2082 \u00b7 China ETS \u2248 {price_cn:.1f} \u20ac/tCO\u2082 "
    f"(Table 4.2 / Fig. 4.4 trajectory, anchored to the 150/32 reference case at 2034)"
)

st.subheader("Technology and electricity scenarios")

col1, col2, col3 = st.columns(3)

# 🔴 BF-BOF baseline
with col1:
    st.write("### BF-BOF (Grid)")
    st.metric("Scope 1", f"{scope1_bf:.2f} tCO₂/t steel")
    st.metric("Scope 2", f"{scope2_bf:.2f} tCO₂/t steel")
    st.metric("Embedded emissions", f"{ee_bf:.2f} tCO₂/t steel")
    st.metric("Production cost", f"{prod_cost_bf:.2f} €/t steel")
    st.metric("Current CBAM", f"{cbam_bf_current:.2f} €/t steel")
    st.metric("Extended CBAM", f"{cbam_bf_extended:.2f} €/t steel")
    st.metric("Total cost (current)", f"{total_bf_current:.2f} €/t steel")
    st.metric("Total cost (extended)", f"{total_bf_extended:.2f} €/t steel")

# 🔵 EAF Grid
with col2:
    st.write("### EAF (Grid)")
    st.metric("Scope 1", f"{scope1_eaf:.2f} tCO₂/t steel")
    st.metric("Scope 2", f"{scope2_eaf_grid:.2f} tCO₂/t steel")
    st.metric("Embedded emissions", f"{ee_eaf_grid:.2f} tCO₂/t steel")
    st.metric("Production cost", f"{prod_cost_eaf_grid:.2f} €/t steel")
    st.metric("Current CBAM", f"{cbam_eaf_grid_current:.2f} €/t steel")
    st.metric("Extended CBAM", f"{cbam_eaf_grid_extended:.2f} €/t steel")
    st.metric("Total cost (current)", f"{total_eaf_grid_current:.2f} €/t steel")
    st.metric("Total cost (extended)", f"{total_eaf_grid_extended:.2f} €/t steel")

# 🟢 EAF Renewable
with col3:
    st.write("### EAF (Renewable)")
    st.metric("Scope 1", f"{scope1_eaf:.2f} tCO₂/t steel")
    st.metric("Scope 2", f"{scope2_eaf_renew:.2f} tCO₂/t steel")
    st.metric("Embedded emissions", f"{ee_eaf_renew:.2f} tCO₂/t steel")
    st.metric("Production cost", f"{prod_cost_eaf_renew:.2f} €/t steel")
    st.metric("Current CBAM", f"{cbam_eaf_renew_current:.2f} €/t steel")
    st.metric("Extended CBAM", f"{cbam_eaf_renew_extended:.2f} €/t steel")
    st.metric("Total cost (current)", f"{total_eaf_renew_current:.2f} €/t steel")
    st.metric("Total cost (extended)", f"{total_eaf_renew_extended:.2f} €/t steel")

# =========================
# Plot 1: Current CBAM
# =========================
st.subheader("CBAM (Current) comparison")

labels = ["BF-BOF (Grid)", "EAF (Grid)", "EAF (Renewable)"]
values = [
    round(cbam_bf_current, 2),
    round(cbam_eaf_grid_current, 2),
    round(cbam_eaf_renew_current, 2)
]

fig, ax = plt.subplots()
colors = ["#9ecae1", "#3182bd", "#31a354"]

ax.bar(labels, values, color=colors)
ax.set_ylabel("€/t steel")
ax.set_title("Current CBAM across technologies")

st.pyplot(fig)

# =========================
# Plot 2: EAF comparison
# =========================
st.subheader("CBAM: Current vs Extended (all routes)")

labels = [
    "BF-Current", "BF-Extended",
    "Grid-Current", "Grid-Extended",
    "Renew-Current", "Renew-Extended"
]

values = [
    round(cbam_bf_current, 2),
    round(cbam_bf_extended, 2),
    round(cbam_eaf_grid_current, 2),
    round(cbam_eaf_grid_extended, 2),
    round(cbam_eaf_renew_current, 2),
    round(cbam_eaf_renew_extended, 2)
]

fig, ax = plt.subplots()
colors = ["#c6dbef", "#9ecae1", "#9ecae1", "#3182bd", "#a1d99b", "#31a354"]

ax.bar(labels, values, color=colors)
ax.set_ylabel("€/t steel")
ax.set_title("CBAM under current vs extended framework")
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

st.pyplot(fig)

# =========================
# Electricity cost
# =========================
st.subheader("Electricity cost comparison")

labels = ["BF-BOF (Grid)", "EAF (Grid)", "EAF (Renewable)"]
values = [
    round(elec_cost_bf, 2),
    round(elec_cost_eaf_grid, 2),
    round(elec_cost_eaf_renew, 2)
]

fig, ax = plt.subplots()

x = np.arange(len(labels))
width = 0.5

ax.bar(x, values, width=width, color=["#9ecae1", "#3182bd", "#31a354"])

ax.set_xticks(x)
ax.set_xticklabels(labels)

ax.set_ylabel("€/t steel")
ax.set_title("Electricity cost component")

st.pyplot(fig)

# =========================
# Plot 4: Total Cost (production + CBAM), current vs extended
# =========================
st.subheader("Total Cost comparison (production + CBAM)")

labels = [
    "BF-Current", "BF-Extended",
    "Grid-Current", "Grid-Extended",
    "Renew-Current", "Renew-Extended"
]

values = [
    round(total_bf_current, 2),
    round(total_bf_extended, 2),
    round(total_eaf_grid_current, 2),
    round(total_eaf_grid_extended, 2),
    round(total_eaf_renew_current, 2),
    round(total_eaf_renew_extended, 2)
]

fig, ax = plt.subplots()
colors = ["#c6dbef", "#9ecae1", "#9ecae1", "#3182bd", "#a1d99b", "#31a354"]

ax.bar(labels, values, color=colors)
ax.set_ylabel("€/t steel")
ax.set_title("Total Cost: production + CBAM, current vs extended framework")
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

st.pyplot(fig)

# =========================
# Insights
# =========================

st.subheader("Key insights")

diff_cbam = cbam_eaf_grid_extended - cbam_eaf_renew_extended
st.write(
    f"Switching from grid to renewable electricity reduces extended CBAM cost by **{round(diff_cbam,2)} €/t steel**."
)

savings_elec = elec_cost_eaf_grid - elec_cost_eaf_renew
if savings_elec > 0:
    st.write(f"Renewable electricity saves **{round(savings_elec,2)} €/t steel** on the electricity component compared to grid electricity (EAF route).")
else:
    st.write(f"Renewable electricity costs **{round(-savings_elec,2)} €/t steel more** than grid electricity on the electricity component (EAF route).")

diff_total_extended = total_eaf_grid_extended - total_eaf_renew_extended
st.write(
    f"Under the extended CBAM framework, EAF with renewable electricity has a **Total Cost {abs(round(diff_total_extended,2))} €/t steel "
    f"{'lower' if diff_total_extended > 0 else 'higher'}** than EAF with grid electricity."
)

diff_bf_eaf_renew_extended = total_bf_extended - total_eaf_renew_extended
st.write(
    f"Under the extended CBAM framework, BF-BOF's Total Cost is **{abs(round(diff_bf_eaf_renew_extended,2))} €/t steel "
    f"{'higher' if diff_bf_eaf_renew_extended > 0 else 'lower'}** than EAF with renewable electricity."
)
