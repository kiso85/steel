import streamlit as st
import matplotlib.pyplot as plt

st.title("CBAM Cost Model")

st.sidebar.header("Input parameters")

# --- Inputs ---
scope1 = st.sidebar.slider("Scope 1 emissions (tCO2/t)", 0.0, 3.0, 0.7)
electricity = st.sidebar.slider("Electricity consumption (kWh/t)", 100, 800, 400)
ef = st.sidebar.slider("Electricity emission factor (tCO2/MWh)", 0.0, 1.0, 0.6)

price_eu = st.sidebar.slider("EU carbon price (€/t)", 50, 200, 120)
price_cn = st.sidebar.slider("China carbon price (€/t)", 0, 100, 30)

benchmark = st.sidebar.slider("Benchmark (tCO2/t)", 0.0, 2.5, 1.3)
cf = st.sidebar.slider("Correction factor", 0.0, 1.0, 0.8)

# --- Calculations ---
scope2 = electricity / 1000 * ef
ee = scope1 + scope2

# Current CBAM (Scope 1 only)
cbam_current = max(scope1 - benchmark * cf, 0) * (price_eu - price_cn)

# Extended CBAM (Scope 1 + Scope 2)
cbam_extended = max(ee - benchmark * cf, 0) * (price_eu - price_cn)

# --- Results ---
st.subheader("Results")

col1, col2 = st.columns(2)

with col1:
    st.metric("Scope 1", round(scope1, 2))
    st.metric("Scope 2", round(scope2, 2))
    st.metric("Embedded emissions", round(ee, 2))

with col2:
    st.metric("CBAM (current)", round(cbam_current, 2))
    st.metric("CBAM (extended)", round(cbam_extended, 2))

# --- Plot ---
st.subheader("CBAM cost comparison")

labels = ["Current CBAM", "Extended CBAM"]
values = [cbam_current, cbam_extended]

fig, ax = plt.subplots()
ax.bar(labels, values)
ax.set_ylabel("€/t steel")
ax.set_title("CBAM cost comparison")

st.pyplot(fig)
