# Visualization Tools

A Python toolbox for data visualization and basic analysis of experimental datasets.

This repository is intended to grow over time as a collection of reusable plotting and analysis tools.

---

## Current Features

- Load CSV data via file picker
- Group data by experimental condition
- Compute summary metrics:
  - Amplitude
  - Duration
  - Area under the curve (AUC)
  - Event rate
- Automatic condition detection
- Reference-based comparisons (first condition in dataset)
- Statistical testing (t-tests vs reference)
- Swarm plot visualizations with mean overlays

---


## Installation
```bash
pip install pandas numpy matplotlib seaborn scipy
```

## Usage
Run the script:
```bash
python csv_to_figures.py
```