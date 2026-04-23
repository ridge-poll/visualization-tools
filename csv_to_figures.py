import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import ttest_ind
import tkinter as tk
from tkinter import filedialog

# ----- File picker -----
root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(
    title="Select CSV file",
    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
)
df = pd.read_csv(file_path)
# -----------------------


# Define condition structure
reference = df["Condition"].iloc[0]
conditions = list(pd.unique(df["Condition"]))
treatments = [c for c in conditions if c != reference]
order = [reference] + treatments

# Summarize data
summary = df.groupby(["Recording", "Condition"]).agg(
    Amplitude=("MaxAmp1", "mean"),
    Duration=("Duration1", "mean"),
    AUC=("AUC1", "mean"),
    EventCount=("Latency1", "count"),
    Start=("Start_s", "first"),
    End=("End_s", "first")
).reset_index()

# Find rate -> events over time 
summary["Rate"] = summary["EventCount"] / (summary["End"] - summary["Start"])
# Find normalized AUC -> AUC over amplitude (currently not wanted by Kojo)
summary["NormAUC"] = summary["AUC"] / summary["Amplitude"]


# Reshape for plotting
long_df = summary.melt(
    id_vars=["Recording", "Condition"],
    value_vars=["Amplitude", "Duration", "AUC", "Rate"],
    var_name="Metric",
    value_name="Value"
)


# color palette
base_colors = ["tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown"]
my_palette = {reference: "tab:blue"}

for cond, color in zip(treatments, base_colors):
    my_palette[cond] = color


# Plotting
metrics = ["Rate", "Amplitude", "Duration", "AUC"]
fig, axes = plt.subplots(1, len(metrics), figsize=(16, 4))
labels = ["Rate of SDs (events/sec)",
          "Negative DC Shift (mV)",
          "SD Duration (sec)",
          "Area under the curve (mV*sec)"]

for ax, m, lbl in zip(axes, metrics, labels):
    subset = long_df[long_df["Metric"] == m]

    sns.swarmplot(
    data=subset,
    x="Condition",
    y="Value",
    hue="Condition",
    palette=my_palette,
    order=order,
    ax=ax,
    size=5,
    legend=False
    )
    # Remove axis labels
    ax.set_xlabel(None)
    ax.set_ylabel(lbl)

    # Mean lines
    for i, cond in enumerate(order):
        values = subset[subset["Condition"] == cond]["Value"]
        if len(values) > 0:
            ax.hlines(values.mean(), i - 0.2, i + 0.2, colors="black")

    # Stats
    control_vals = subset[subset["Condition"] == reference]["Value"]

    p_text = []
    for cond in treatments:
        group_vals = subset[subset["Condition"] == cond]["Value"]

        if len(control_vals) > 1 and len(group_vals) > 1:
            _, pval = ttest_ind(control_vals, group_vals, nan_policy="omit")
            p_text.append(f"p={pval:.3f}")

    ax.set_title(f"{m}\n" + "\n".join(p_text))

plt.tight_layout()
plt.show()