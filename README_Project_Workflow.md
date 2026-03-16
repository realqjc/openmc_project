# OpenMC Reactor Simulation Project

This project contains Python scripts for running and analyzing OpenMC simulations of a simplified reactor pin cell.

The project supports automated parameter scans (fuel enrichment and lattice pitch), automatic analysis, and configurable workflows using a YAML configuration file.

---

# 1. Project Overview

The project is designed around three main ideas:

1. **Configuration-driven simulation**
2. **Automatic directory management**
3. **Automated analysis workflow**

All important parameters are defined in:


project_config.yaml


The simulation scripts read this configuration instead of hard-coding parameters.

---

# 2. Project Directory Structure


openmc_project/
│
├── .vscode/
│ ├── settings.json
│ └── tasks.json
│
├── scripts/
│ ├── common_paths.py
│ ├── config_loader.py
│ ├── test_openmc6.py
│ ├── test_openmc7.py
│ ├── analyze_pitch_results.py
│ ├── analyze_enrichment_results.py
│ ├── run_all_analysis.py
│ ├── run_full_reactor_study.py
│ └── clean_old_statepoints.py
│
├── input/
│ OpenMC generated XML files
│
├── results/
│ Simulation results (CSV + plots)
│
├── statepoints/
│ OpenMC statepoint output (.h5)
│
├── project_config.yaml
├── README_Project_Workflow.md
└── project_structure.md


---

# 3. Configuration System

All simulation parameters are defined in:


project_config.yaml


This file contains:

### simulation settings


settings:
batches
inactive
particles


### geometry parameters


geometry:
fuel_radius
clad_radius


### scan configuration


pitch_scan
enrichment_scan


### analysis configuration


analysis


### workflow configuration


workflow


The configuration file is read by:


scripts/config_loader.py


This allows modifying simulation parameters **without editing Python scripts**.

---

# 4. Simulation Scripts

## test_openmc6.py

Performs **pin pitch scan**.

Parameters are read from:


project_config.yaml → pitch_scan


Outputs:


results/pitch_scan/


Files generated:


pitch_keff_results_TIMESTAMP.csv
keff_pitch_TIMESTAMP.png


Statepoint files are stored in:


statepoints/pitch_scan/


Each pitch value has its own directory.

---

## test_openmc7.py

Performs **fuel enrichment scan**.

Parameters are read from:


project_config.yaml → enrichment_scan


Outputs:


results/enrichment_scan/


Files generated:


enrichment_keff_results_TIMESTAMP.csv
keff_enrichment_TIMESTAMP.png


Statepoint files:


statepoints/enrichment_scan/


---

# 5. Analysis Scripts

Simulation results are analyzed automatically.

---

## analyze_enrichment_results.py

Analyzes enrichment scan results.

Features:

- reads latest CSV
- plots k-effective vs enrichment
- estimates **critical enrichment (k=1)**
- generates analysis report

Outputs:


results/enrichment_scan/analysis/


---

## analyze_pitch_results.py

Analyzes pitch scan results.

Features:

- reads latest CSV
- plots k-effective vs pitch
- finds **best pitch**

Outputs:


results/pitch_scan/analysis/


---

# 6. Analysis Controller

## run_all_analysis.py

Runs all enabled analysis scripts.

Enabled scans are determined by:


project_config.yaml


Example:


python scripts/run_all_analysis.py


---

# 7. Full Workflow Controller

## run_full_reactor_study.py

This script controls the **entire simulation workflow**.

Steps:

1. read configuration
2. run enabled scans
3. run analysis
4. optionally clean old statepoints

Example:


python scripts/run_full_reactor_study.py


---

# 8. Cleaning Old Simulation Data

OpenMC statepoints can accumulate and consume disk space.

Use:


clean_old_statepoints.py


Preview old directories:


python scripts/clean_old_statepoints.py


Delete directories older than 7 days:


python scripts/clean_old_statepoints.py --days 7 --delete


Automatic cleanup can be configured in:


project_config.yaml → workflow


---

# 9. Recommended Workflow

Typical usage:

### Run full study


python scripts/run_full_reactor_study.py


or via VS Code task:


Run Full Reactor Study


---

### Run only scans


python scripts/test_openmc6.py
python scripts/test_openmc7.py


---

### Run analysis only


python scripts/run_all_analysis.py


---

### Clean statepoints


python scripts/clean_old_statepoints.py


---

# 10. Important Notes

- Never manually modify files in `statepoints/`
- Always use cleanup scripts
- CSV files in `results/` contain final numerical results

---

# 11. Future Extensions

Possible future improvements:

- moderator density scan
- fuel radius scan
- automatic report generation
- multi-parameter optimization
- Git version control integration