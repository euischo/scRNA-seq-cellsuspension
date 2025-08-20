import streamlit as st
import pandas as pd

def calculate_pbs_for_target(samples, target_concentration, target_recovery, final_volume_per_sample=100):
    result = []
    pool_total_cells = 0
    pool_total_volume = 0

    for sample in samples:
        cell_count = sample["cell_count"]
        required_total_vol = cell_count / target_concentration
        pbs_to_add = required_total_vol - final_volume_per_sample
        pbs_to_add = max(0, round(pbs_to_add, 2))  # No negative volume
        result.append({
            "Sample Name": sample["name"],
            "Cell Count": cell_count,
            "PBS to Add (uL)": pbs_to_add,
            "Final Volume (uL)": final_volume_per_sample + pbs_to_add
        })
        pool_total_cells += cell_count
        pool_total_volume += final_volume_per_sample + pbs_to_add

    final_concentration = pool_total_cells / pool_total_volume
    withdraw_volume = round(target_recovery / final_concentration, 2)

    summary = {
        "Total Pool Volume (uL)": round(pool_total_volume, 2),
        "Total Cells": int(pool_total_cells),
        "Final Pool Concentration (cells/uL)": round(final_concentration, 2),
        "Withdraw Volume for Target Recovery (uL)": withdraw_volume
    }

    return result, summary

# Streamlit UI
st.title("의선이의 scRNA-sequencing cell suspension volume calculator <3")
st.markdown("Calculate PBS volume to dilute your samples to a common target cell concentration.")

n_samples = st.number_input("Number of Samples to Pool (max 8):", min_value=1, max_value=8, value=4)
target_concentration = st.number_input("Target Cell Concentration (cells/μL):", min_value=200, max_value=2000, value=1300)
target_recovery = st.number_input("Target Cell Recovery (total cells):", min_value=10000, max_value=20000, value=20000)

samples = []
st.subheader("Input Cell Counts for Each Sample")
for i in range(n_samples):
    name = st.text_input(f"Sample {i+1} Name:", value=f"S{i+1}")
    cell_count = st.number_input(f"Sample {i+1} Cell Count:", min_value=10000, value=130000, key=f"count_{i}")
    samples.append({"name": name, "cell_count": cell_count})

if st.button("Calculate"):
    results, summary = calculate_pbs_for_target(samples, target_concentration, target_recovery)
    df_results = pd.DataFrame(results)
    st.subheader("PBS Volume per Sample")
    st.dataframe(df_results)

    st.subheader("Summary of Pooled Suspension")
    st.json(summary)

    st.bar_chart(df_results.set_index("Sample Name")["PBS to Add (uL)"])

st.markdown("Developed for scRNA-seq cell prep planning. 멋지죠.")
