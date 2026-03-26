import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
st.title("EAF-Based CBAM and Electricity Cost Model")

# =========================
# Sidebar inputs
# =========================
st.sidebar.header("Input parameters")

# EAF share
w_eaf = st.sidebar.slider("EAF share", 0.0, 1.0, 1.0)

# Technology-specific parameters
s1_eaf = 0.12
s1_bf = 2.20

e_eaf = st.sidebar.slider(
    "EAF electricity consumption (kWh/t steel)",
    300, 600, 400
)
e_bf = 80

# Weighted average based on technology mix
scope1 = w_eaf * s1_eaf + (1 - w_eaf) * s1_bf
electricity = w_eaf * e_eaf + (1 - w_eaf) * e_bf

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

st.sidebar.subheader("Electricity price")
price_grid = st.sidebar.slider("Grid price (€/MWh)", 40, 120, 70)
lcoe_renew = st.sidebar.slider("Renewable LCOE (€/MWh)", 25, 40, 32)
extra_cost = st.sidebar.slider(
    "Additional renewable system cost (€/MWh)",
    0, 40, 15
)
price_renew = lcoe_renew + extra_cost
# =========================
# Renewable electricity assumptions
# =========================
st.sidebar.subheader("Renewable electricity assumptions")

alpha = st.sidebar.slider(
    "Self-consumption ratio",
    0.6, 1.0, 0.7
)

price_sell = st.sidebar.slider(
    "Export electricity price (€/MWh)",
    0, 100, 40
)
# =========================
# Calculations
# =========================

# Scope 2
scope2_grid = electricity / 1000 * ef_grid
scope2_renew = electricity / 1000 * ef_renew

# Embedded emissions
ee_grid = scope1 + scope2_grid
ee_renew = scope1 + scope2_renew

# Current CBAM (Scope 1 only)
cbam_current_grid = (scope1 - benchmark * cf) * (price_eu - price_cn)
cbam_current_renew = cbam_current_grid  # same value

# Extended CBAM (Scope 1 + Scope 2)
cbam_extended_grid = (ee_grid - benchmark * cf) * (price_eu - price_cn)
cbam_extended_renew = (ee_renew - benchmark * cf) * (price_eu - price_cn)

# =========================
# Results display
# =========================
st.subheader("Electricity sourcing scenarios")

col1, col2 = st.columns(2)

with col1:
    st.write("### Grid electricity")
    st.metric("Scope 1", f"{s1_eaf:.2f} <span style='font-size:12px'>tCO₂/t steel</span>", unsafe_allow_html=True)
    st.metric("Scope 2", f"{scope2_grid:.2f} <span style='font-size:12px'>tCO₂/t steel</span>", unsafe_allow_html=True)
    st.metric("Embedded emissions", f"{ee_grid:.2f} <span style='font-size:12px'>tCO₂/t steel</span>", unsafe_allow_html=True)
    st.metric("Current CBAM", f"{cbam_current_grid:.2f} <span style='font-size:12px'>€/t steel</span>", unsafe_allow_html=True)
    st.metric("Extended CBAM", f"{cbam_extended_grid:.2f} <span style='font-size:12px'>€/t steel</span>", unsafe_allow_html=True)

with col2:
    st.write("### Renewable electricity")
    st.metric("Scope 1", f"{s1_eaf:.2f} <span style='font-size:12px'>tCO₂/t steel</span>", unsafe_allow_html=True)
    st.metric("Scope 2", f"{scope2_renew:.2f} <span style='font-size:12px'>tCO₂/t steel</span>", unsafe_allow_html=True)
    st.metric("Embedded emissions", f"{ee_renew:.2f} <span style='font-size:12px'>tCO₂/t steel</span>", unsafe_allow_html=True)
    st.metric("Current CBAM", f"{cbam_current_renew:.2f} <span style='font-size:12px'>€/t steel</span>", unsafe_allow_html=True)
    st.metric("Extended CBAM", f"{cbam_extended_renew:.2f} <span style='font-size:12px'>€/t steel</span>", unsafe_allow_html=True)

# =========================
# Plot
# =========================
st.subheader("CBAM cost comparison")

labels = [
    "Grid-Current",
    "Grid-Extended",
    "Renew-Current",
    "Renew-Extended"
]

values = [
    round(cbam_current_grid, 2),
    round(cbam_extended_grid, 2),
    round(cbam_current_renew, 2),
    round(cbam_extended_renew, 2)
]

fig, ax = plt.subplots()
colors = ["#9ecae1", "#3182bd", "#a1d99b", "#31a354"]
ax.bar(labels, values, color=colors)
ax.set_ylabel("€/t steel")
ax.set_title("CBAM cost under different electricity sourcing")
    
st.pyplot(fig)
# =========================
# Insight
# =========================
st.subheader("Key insight")

diff = cbam_extended_grid - cbam_extended_renew

st.write(
    f"Switching from grid to renewable electricity reduces extended CBAM cost by **{round(diff,2)} €/t steel**."
)


# =========================
# Electricity cost (ADD THIS)
# =========================
price_renew_effective = max(
    (price_renew - min(1-alpha,0.2) * price_sell) / alpha,
    0
)
elec_cost_grid = electricity / 1000 * price_grid
elec_cost_renew = electricity / 1000 * price_renew_effective
# =========================
# Plot: Electricity Cost Only (EAF)
# =========================

st.subheader("Electricity cost comparison")

labels = [
    "Grid Electricity",
    "Renewable Electricity"
]

values = [
    round(elec_cost_grid, 2),
    round(elec_cost_renew, 2)
]

fig, ax = plt.subplots()
x = np.array([-0.25, 0.25])
width = 0.22
fig, ax = plt.subplots()
ax.bar(x, values, width=width, color=["#3182bd", "#31a354"])

ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel("Electricity Cost (€/t steel)")
ax.set_title("Electricity Cost by Source")

st.pyplot(fig)
# =========================
# Key insight: cost savings
# =========================

savings = elec_cost_grid - elec_cost_renew

st.subheader("Key Insight")

if savings > 0:
    st.write(f"Renewable electricity saves **{round(savings,2)} €/t steel** compared to grid electricity.")
else:
    st.write(f"Renewable electricity costs **{round(-savings,2)} €/t steel more** than grid electricity.")
