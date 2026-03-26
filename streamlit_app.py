import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: 20px;
}
</style>
""", unsafe_allow_html=True)
st.title("CBAM Cost Comparison Model (BF vs EAF)")

# =========================
# Sidebar inputs
# =========================
st.sidebar.header("Input parameters")

# Technology-specific parameters
s1_eaf = 0.12
s1_bf = 2.18

e_eaf = st.sidebar.slider(
    "EAF electricity consumption (kWh/t steel)",
    300, 600, 400
)
e_bf = 80

# Electricity sourcing
st.sidebar.subheader("Electricity emission factors")
ef_grid = st.sidebar.slider("Grid emission factor (tCO2/MWh)", 0.4, 1.0, 0.8)
ef_renew = st.sidebar.slider("Renewable emission factor (tCO2/MWh)", 0.0, 0.05, 0.02)

# Carbon prices
st.sidebar.subheader("Carbon prices")
price_eu = st.sidebar.slider("EU carbon price (€/t)", 50, 200, 150)
price_cn = st.sidebar.slider("China carbon price (€/t)", 0, 100, 32)

# CBAM parameters
st.sidebar.subheader("CBAM parameters")
benchmark = st.sidebar.slider("Benchmark (tCO2/t)", 0.0, 2.5, 1.3)
cf = st.sidebar.slider("CBAM factor", 0.0, 1.0, 0.0)

# Electricity price
st.sidebar.subheader("Electricity price")
price_grid = st.sidebar.slider("Grid price (€/MWh)", 40, 120, 70)
lcoe_renew = st.sidebar.slider("Renewable LCOE (€/MWh)", 25, 40, 32)
extra_cost = st.sidebar.slider("Additional renewable system cost (€/MWh)", 0, 40, 15)
price_renew = lcoe_renew + extra_cost

# Renewable assumptions
st.sidebar.subheader("Renewable electricity assumptions")
alpha = st.sidebar.slider("Self-consumption ratio", 0.6, 1.0, 0.7)
price_sell = st.sidebar.slider("Export electricity price (€/MWh)", 0, 100, 40)

# =========================
# Scenario calculations
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
# CBAM calculations
# =========================

# Current CBAM (Scope 1 only)
cbam_bf_current = (scope1_bf - benchmark * cf) * (price_eu - price_cn)
cbam_eaf_grid_current = (scope1_eaf - benchmark * cf) * (price_eu - price_cn)
cbam_eaf_renew_current = cbam_eaf_grid_current

# Extended CBAM (EAF only)
cbam_eaf_grid_extended = (ee_eaf_grid - benchmark * cf) * (price_eu - price_cn)
cbam_eaf_renew_extended = (ee_eaf_renew - benchmark * cf) * (price_eu - price_cn)

# =========================
st.subheader("Technology and electricity scenarios")

col1, col2, col3 = st.columns(3)

# 🔴 BF-BOF baseline
with col1:
    st.write("### BF-BOF (Grid)")
    st.metric("Scope 1", f"{scope1_bf:.2f} tCO₂/t steel")
    st.metric("Scope 2", f"{scope2_bf:.2f} tCO₂/t steel")
    st.metric("Embedded emissions", f"{ee_bf:.2f} tCO₂/t steel")
    st.metric("Current CBAM", f"{cbam_bf_current:.2f} €/t steel")
    st.metric("Extended CBAM", f"{cbam_bf_current:.2f} €/t steel")  # 可选（或删掉）

# 🔵 EAF Grid
with col2:
    st.write("### EAF (Grid)")
    st.metric("Scope 1", f"{scope1_eaf:.2f} tCO₂/t steel")
    st.metric("Scope 2", f"{scope2_eaf_grid:.2f} tCO₂/t steel")
    st.metric("Embedded emissions", f"{ee_eaf_grid:.2f} tCO₂/t steel")
    st.metric("Current CBAM", f"{cbam_eaf_grid_current:.2f} €/t steel")
    st.metric("Extended CBAM", f"{cbam_eaf_grid_extended:.2f} €/t steel")

# 🟢 EAF Renewable
with col3:
    st.write("### EAF (Renewable)")
    st.metric("Scope 1", f"{scope1_eaf:.2f} tCO₂/t steel")
    st.metric("Scope 2", f"{scope2_eaf_renew:.2f} tCO₂/t steel")
    st.metric("Embedded emissions", f"{ee_eaf_renew:.2f} tCO₂/t steel")
    st.metric("Current CBAM", f"{cbam_eaf_renew_current:.2f} €/t steel")
    st.metric("Extended CBAM", f"{cbam_eaf_renew_extended:.2f} €/t steel")
    
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
st.subheader("EAF: Current vs Extended CBAM")

labels = [
    "Grid-Current",
    "Grid-Extended",
    "Renew-Current",
    "Renew-Extended"
]

values = [
    round(cbam_eaf_grid_current, 2),
    round(cbam_eaf_grid_extended, 2),
    round(cbam_eaf_renew_current, 2),
    round(cbam_eaf_renew_extended, 2)
]

fig, ax = plt.subplots()
colors = ["#9ecae1", "#3182bd", "#a1d99b", "#31a354"]

ax.bar(labels, values, color=colors)
ax.set_ylabel("€/t steel")
ax.set_title("CBAM for EAF under different electricity sourcing")

st.pyplot(fig)

# =========================
# Electricity cost
# =========================

price_renew_effective = max(
    (price_renew - min(1 - alpha, 0.2) * price_sell) / alpha,
    0
)

elec_cost_grid = e_eaf / 1000 * price_grid
elec_cost_renew = e_eaf / 1000 * price_renew_effective

st.subheader("Electricity cost comparison")

labels = ["Grid Electricity", "Renewable Electricity"]
values = [
    round(elec_cost_grid, 2),
    round(elec_cost_renew, 2)
]

fig, ax = plt.subplots()
ax.bar(labels, values, color=["#3182bd", "#31a354"])

ax.set_ylabel("€/t steel")
ax.set_title("Electricity Cost (EAF)")

st.pyplot(fig)

# =========================
# Insights
# =========================

st.subheader("Key insights")

diff = cbam_eaf_grid_extended - cbam_eaf_renew_extended
st.write(
    f"Switching from grid to renewable electricity reduces extended CBAM cost by **{round(diff,2)} €/t steel**."
)

savings = elec_cost_grid - elec_cost_renew

if savings > 0:
    st.write(f"Renewable electricity saves **{round(savings,2)} €/t steel** compared to grid electricity.")
else:
    st.write(f"Renewable electricity costs **{round(-savings,2)} €/t steel more** than grid electricity.")
