# 为github首页说明，非详细说明。详细说明参见README_Project_Workflow.md和project_structure.md

# OpenMC automated reactor parameter scan framework

This project contains Python scripts for performing automated **OpenMC reactor pin-cell simulations**.

The code supports parameter scans of:

- fuel enrichment
- lattice pitch

and automatically organizes simulation outputs and analysis results.

The project is designed for **learning OpenMC modeling and automated reactor parameter studies**.

---

# Project Features

The project implements:

- automated OpenMC simulations
- parameter scanning
- automatic directory management
- automatic data analysis
- configuration-driven workflow
- VS Code task integration

All simulation parameters are controlled through a single configuration file:


project_config.yaml


This allows modifying scan ranges without editing Python scripts.

---

# Example Studies

The scripts can perform studies such as:

### Fuel enrichment scan


U-235 enrichment: 0.2% → 2.0%


Result:


k-effective vs enrichment
critical enrichment estimate


---

### Lattice pitch scan


pitch: 0.95 cm → 4.50 cm


Result:


k-effective vs pitch
optimal lattice pitch


---

# Project Structure


openmc_project
│
├── scripts/ Python simulation and analysis scripts
├── input/ OpenMC XML input files
├── results/ CSV results and plots
├── statepoints/ OpenMC output files (.h5)
│
├── project_config.yaml central configuration file
├── README.md
├── README_Project_Workflow.md
└── project_structure.md


Detailed descriptions can be found in:


README_Project_Workflow.md
project_structure.md


---

# Installation

Recommended environment:


conda create -n openmc-x86 python
conda activate openmc-x86
conda install -c conda-forge openmc numpy matplotlib
pip install pyyaml


Or install dependencies from:


pip install -r requirements.txt


---

# Running Simulations

## Run full automated workflow


python scripts/run_full_reactor_study.py


This will automatically:


run pitch scan
run enrichment scan
run analysis
(optional) clean old statepoints


All behavior is controlled by:


project_config.yaml


---

## Run individual scans

Pitch scan:


python scripts/test_openmc6.py


Enrichment scan:


python scripts/test_openmc7.py


---

## Run analysis only


python scripts/run_all_analysis.py


---

## Clean old statepoints

Preview old simulation folders:


python scripts/clean_old_statepoints.py


Delete directories older than 7 days:


python scripts/clean_old_statepoints.py --days 7 --delete


---

# VS Code Integration

The project includes predefined VS Code tasks.

Press:


Cmd + Shift + B


Available tasks:


Run Pitch Scan
Run Enrichment Scan
Analyze All Results
Clean Old Statepoints
Run Full Reactor Study


---

# Output Data

Simulation results are stored in:


results/


Example:


results/enrichment_scan/
results/pitch_scan/


Each run produces timestamped files to avoid overwriting older results.

Example:


pitch_keff_results_2026-03-14_013200.csv


Plots and analysis results are also saved automatically.

---

# Learning Goals

This project was built for:

- learning OpenMC reactor modeling
- understanding Monte Carlo criticality calculations
- practicing parameter scanning
- building automated scientific workflows

---

# Future Extensions

Possible improvements:

- moderator density scan
- fuel radius optimization
- automatic report generation
- multi-parameter optimization
- parallel scan execution