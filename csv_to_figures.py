import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import ttest_rel
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

# Force pairs to exist
all_pairs = pd.MultiIndex.from_product(
    [df["Recording"].unique(), df["Condition"].unique()],
    names=["Recording", "Condition"]
)

# Summarize data
summary = df.groupby(["Recording", "Condition"]).agg(
    Amplitude=("MaxAmp1", "mean"),
    Duration=("Duration1", "mean"),
    ShiftSlope=("ShiftSlope1", "mean"),
    AUC=("AUC1", "mean"),
    EventCount=("Duration1", "count"),
    Start=("Start_s", "first"),
    End=("End_s", "first")
).reindex(all_pairs).reset_index()


# Fix event count (missing -> 0 events)
summary["EventCount"] = summary["EventCount"].fillna(0)

# Find rate -> events over time 
duration = summary["End"] - summary["Start"]
summary["Rate"] = np.where((summary["EventCount"] > 0) &
                           (duration > 0),summary["EventCount"] / duration,0)

# Find normalized AUC -> AUC over amplitude (currently not wanted by Kojo)
summary["NormAUC"] = summary["AUC"] / summary["Amplitude"]


# Reshape for plotting
long_df = summary.melt(
    id_vars=["Recording", "Condition"],
    value_vars=["Amplitude", "Duration", "ShiftSlope", "AUC", "Rate"],
    var_name="Metric",
    value_name="Value"
)


# color palette
base_colors = ["tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown"]
my_palette = {reference: "tab:blue"}

for cond, color in zip(treatments, base_colors):
    my_palette[cond] = color


# Plotting
metrics = ["Rate", "Amplitude", "Duration", "ShiftSlope", "AUC"]

fig, axes = plt.subplots(1, len(metrics), figsize=(12, 3))
labels = ["Rate of SDs (events/sec)",
          "Negative DC Shift (mV)",
          "SD Duration (sec)",
          "Steepest Slope of SD (mV/sec)",
          "Area Under the Curve (mV*sec)"]

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
    p_text = []

    control_df = subset[subset["Condition"] == reference][["Recording", "Value"]]
    for cond in treatments:
        group_df = subset[subset["Condition"] == cond][["Recording", "Value"]]

        merged = pd.merge(
            control_df,
            group_df,
            on="Recording",
            suffixes=("_control", "_treat")
        )
        merged = merged.dropna(subset=["Value_control", "Value_treat"])
        

        if len(merged) > 1:
            _, pval = ttest_rel(
                merged["Value_control"],
                merged["Value_treat"],
                nan_policy="omit"
            )
            p_text.append(f"{cond}: p={pval:.3f}")
        else:
            p_text.append(f"{cond}: n too small")

    ax.set_title(f"{m}\n" + "\n".join(p_text))

plt.tight_layout()
plt.show()