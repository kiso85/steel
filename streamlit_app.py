import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd



st.title("CBAM Cost Comparison Model")

# =========================
# Sidebar inputs
# =========================
st.sidebar.header("Input parameters")

scope1 = st.sidebar.slider("Scope 1 emissions (tCO2/t)", 0.0, 3.0, 0.7)
electricity = st.sidebar.slider("Electricity consumption (kWh/t)", 100, 800, 400)

# Electricity sourcing
st.sidebar.subheader("Electricity emission factors")
ef_grid = st.sidebar.slider("Grid emission factor (tCO2/MWh)", 0.4, 1.0, 0.6)
ef_renew = st.sidebar.slider("Renewable emission factor (tCO2/MWh)", 0.0, 0.2, 0.05)

# Carbon prices
st.sidebar.subheader("Carbon prices")
price_eu = st.sidebar.slider("EU carbon price (€/t)", 50, 200, 120)
price_cn = st.sidebar.slider("China carbon price (€/t)", 0, 100, 30)

# CBAM parameters
st.sidebar.subheader("CBAM parameters")
benchmark = st.sidebar.slider("Benchmark (tCO2/t)", 0.0, 2.5, 1.3)
cf = st.sidebar.slider("CBAM factor", 0.0, 1.0, 0.8)

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
st.subheader("CBAM comparison")

col1, col2 = st.columns(2)

with col1:
    st.write("### Grid electricity")
    st.metric("Scope 2", round(scope2_grid, 2))
    st.metric("Embedded emissions", round(ee_grid, 2))
    st.metric("Current CBAM", round(cbam_current_grid, 2))
    st.metric("Extended CBAM", round(cbam_extended_grid, 2))

with col2:
    st.write("### Renewable electricity")
    st.metric("Scope 2", round(scope2_renew, 2))
    st.metric("Embedded emissions", round(ee_renew, 2))
    st.metric("Current CBAM", round(cbam_current_renew, 2))
    st.metric("Extended CBAM", round(cbam_extended_renew, 2))

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
ax.bar(labels, values)
ax.set_ylabel("€/t steel")
ax.set_title("CBAM cost under different electricity sourcing")

df = pd.DataFrame({
    "Scenario": ["Grid-Current", "Grid-Extended", "Renew-Current", "Renew-Extended"],
    "CBAM cost (€/t)": values
})

st.table(df)
    
st.pyplot(fig)

# =========================
# Insight
# =========================
st.subheader("Key insight")

diff = cbam_extended_grid - cbam_extended_renew

st.write(
    f"Switching from grid to renewable electricity reduces extended CBAM cost by **{round(diff,2)} €/t steel**."
)
