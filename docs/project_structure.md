# Project Structure

This document describes the directory structure of the OpenMC reactor simulation project.

---

# Root Directory


openmc_project


Main folders:


.vscode
scripts
input
results
statepoints


---

# .vscode

Contains VS Code configuration files.


.vscode/
│
├── settings.json
└── tasks.json


`tasks.json` defines tasks such as:

- Run Pitch Scan
- Run Enrichment Scan
- Analyze Results
- Run Full Reactor Study

---

# scripts

Contains all Python scripts used for the project.


scripts/
│
├── common_paths.py
├── config_loader.py
├── test_openmc6.py
├── test_openmc7.py
├── analyze_pitch_results.py
├── analyze_enrichment_results.py
├── run_all_analysis.py
├── run_full_reactor_study.py
└── clean_old_statepoints.py


---

## common_paths.py

Defines important project paths:


INPUT_DIR
RESULTS_DIR
STATEPOINTS_DIR


Also provides helper functions:


make_scan_dirs()
working_directory()


---

## config_loader.py

Loads the project configuration:


project_config.yaml


This allows scripts to read parameters without hardcoding them.

---

## test_openmc6.py

Simulation script for **pitch scan**.

Reads parameters from:


project_config.yaml → pitch_scan


---

## test_openmc7.py

Simulation script for **enrichment scan**.

Reads parameters from:


project_config.yaml → enrichment_scan


---

## analyze scripts


analyze_pitch_results.py
analyze_enrichment_results.py


These scripts analyze simulation outputs and produce plots and reports.

---

## run_all_analysis.py

Runs all analysis scripts automatically.

---

## run_full_reactor_study.py

Controls the entire workflow:


scan → analysis → optional cleanup


---

## clean_old_statepoints.py

Utility script to remove old OpenMC statepoint files.

---

# input


input/


Stores OpenMC XML files generated during simulations.

Typical files:


model.xml
geometry.xml
materials.xml
settings.xml
plots.xml


---

# results


results/


Contains simulation outputs.

Subfolders:


results/pitch_scan
results/enrichment_scan


Each scan produces:


CSV result files
PNG plots
analysis results


---

# statepoints


statepoints/


Stores OpenMC statepoint output files (`.h5`).

Subfolders correspond to simulation scans.

Example:


statepoints/pitch_scan/pitch_1.50
statepoints/enrichment_scan/enrichment_1.20


---

# Configuration File


project_config.yaml


Central configuration file controlling:

- simulation settings
- geometry parameters
- scan ranges
- analysis behavior
- workflow automation

---

# Documentation


README_Project_Workflow.md
project_structure.md


These files describe:

- project workflow
- directory structure
- usage instructions