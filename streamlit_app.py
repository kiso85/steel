import streamlit as st
import matplotlib.pyplot as plt

st.title("EAF-Based CBAM + Total Cost Model")

# =========================
# Sidebar inputs
# =========================
st.sidebar.header("Input parameters")

# EAF share
w_eaf = st.sidebar.slider("EAF share", 0.0, 1.0, 1.0)

# Technology-specific parameters
s1_eaf = 0.18
s1_bf = 2.20

e_eaf = 400   # kWh/t
e_bf = 80

# Weighted
scope1 = w_eaf * s1_eaf + (1 - w_eaf) * s1_bf
electricity = w_eaf * e_eaf + (1 - w_eaf) * e_bf

# =========================
# Electricity parameters
# =========================
st.sidebar.subheader("Electricity emission factors")
ef_grid = st.sidebar.slider("Grid EF (tCO2/MWh)", 0.4, 1.0, 0.8)
ef_renew = st.sidebar.slider("Renewable EF", 0.0, 0.05, 0.02)

st.sidebar.subheader("Electricity price")
price_grid = st.sidebar.slider("Grid price (€/MWh)", 40, 120, 70)
price_renew = st.sidebar.slider("Renewable price (€/MWh)", 20, 100, 55)

# =========================
# Carbon prices
# =========================
st.sidebar.subheader("Carbon prices")
price_eu = st.sidebar.slider("EU carbon price", 50, 200, 150)
price_cn = st.sidebar.slider("China carbon price", 0, 100, 32)

# =========================
# CBAM parameters
# =========================
st.sidebar.subheader("CBAM parameters")
benchmark = st.sidebar.slider("Benchmark", 0.0, 2.5, 1.3)
cf = st.sidebar.slider("CBAM factor", 0.0, 1.0, 0.0)

# =========================
# Calculations
# =========================

# Scope 2
scope2_grid = electricity / 1000 * ef_grid
scope2_renew = electricity / 1000 * ef_renew

# Embedded emissions
ee_grid = scope1 + scope2_grid
ee_renew = scope1 + scope2_renew

# Electricity cost
elec_cost_grid = electricity / 1000 * price_grid
elec_cost_renew = electricity / 1000 * price_renew

# -------------------------
# CBAM
# -------------------------

# Current CBAM (Scope 1)
cbam_current = (scope1 - benchmark * cf) * (price_eu - price_cn)

# Extended CBAM
cbam_ext_grid = (ee_grid - benchmark * cf) * (price_eu - price_cn)
cbam_ext_renew = (ee_renew - benchmark * cf) * (price_eu - price_cn)

# -------------------------
# Total cost
# -------------------------
total_grid = cbam_ext_grid + elec_cost_grid
total_renew = cbam_ext_renew + elec_cost_renew

# =========================
# Results display
# =========================
st.subheader("Results")

col1, col2 = st.columns(2)

with col1:
    st.write("### Grid electricity")
    st.metric("Scope 1", round(scope1, 2))
    st.metric("Scope 2", round(scope2_grid, 2))
    st.metric("CBAM (extended)", round(cbam_ext_grid, 2))
    st.metric("Electricity cost", round(elec_cost_grid, 2))
    st.metric("Total cost", round(total_grid, 2))

with col2:
    st.write("### Renewable electricity")
    st.metric("Scope 1", round(scope1, 2))
    st.metric("Scope 2", round(scope2_renew, 2))
    st.metric("CBAM (extended)", round(cbam_ext_renew, 2))
    st.metric("Electricity cost", round(elec_cost_renew, 2))
    st.metric("Total cost", round(total_renew, 2))

# =========================
# Plot
# =========================
st.subheader("Total cost comparison")

labels = [
    "Grid Total",
    "Renewable Total"
]

values = [
    round(total_grid, 2),
    round(total_renew, 2)
]

fig, ax = plt.subplots()
ax.bar(labels, values)
ax.set_ylabel("€/t steel")
ax.set_title("Total cost comparison")

st.pyplot(fig)

# =========================
# Insight
# =========================
st.subheader("Key insight")

diff = total_grid - total_renew

if diff > 0:
    st.write(f"Renewable is cheaper by **{round(diff,2)} €/t steel**")
else:
    st.write(f"Grid is cheaper by **{round(-diff,2)} €/t steel**")
