# Spatio-Temporal Modelling of Electric Vehicle Charging Demand

This repository contains the research code accompanying the paper:

Bouaachra K., Goude Y., Amara Ouali Y., Lachieze-Rey R.  
*Spatio-Temporal Modelling of Electric Vehicle Charging Demand*
---
## Overview

Accurate forecasting of electric vehicle (EV) charging demand is critical for grid management and infrastructure planning in rapidly evolving EV ecosystems.

This project introduces a new EV dataset collected in Scotland (2022–2025) and proposes a spatio-temporal modelling framework based on latent Gaussian fields. Bayesian inference is performed using Integrated Nested Laplace Approximation (INLA), enabling scalable uncertainty quantification and structured modelling of spatial and temporal dependencies.

The repository includes preprocessing scripts, model implementation, and evaluation procedures to ensure internal reproducibility of the study.

Note: Raw data are publicly available through the ChargePlace Scotland portal. Any derived datasets used in this study are processed versions collected through the provided pipeline in the paper.
---
## Data Description and Provenance

### Data Source

The empirical foundation of this study is a high-resolution longitudinal dataset of Electric Vehicle (EV) charging events in Scotland.

The raw charging records were obtained from the open-access platform  
ChargePlace Scotland (2025), the national public charging network database.

The dataset covers the period:

October 2022 – April 2025

This temporal window was deliberately selected to capture recent distribution shifts in EV adoption and charging behaviour, ensuring relevance to current infrastructure planning challenges.

### Rationale for Dataset Selection

The dataset was chosen according to three main criteria:

1. **Transparency**  
   The open-access nature of the source ensures reproducibility of the preprocessing pipeline and auditability of the results.

2. **Temporal Fidelity**  
   The recent time span captures evolving charging patterns and network expansion effects.

3. **Novelty**  
   This specific temporal window has not been previously used as a benchmark for spatio-temporal EV demand modelling.

### Data Enrichment

To enhance the raw telemetry, several relational integrations were performed:

- Charging point identifiers were linked to connector specifications and postcode information using metadata from Davies et al. (2024).
- Geographic context was incorporated using official spatial boundaries provided by Open Data Scotland (Improvement Service, 2025).

---
## Repository Structure

The repository is organized as follows:

### Analysis
Contains the Jupyter notebook for exploratory data analysis and initial investigations.
- `analysis.ipynb` – Main EDA notebook examining distributions, correlations, and initial patterns in the EV charging dataset.

### datasets


The datasets supporting the findings of this study are publicly available on Zenodo:  
[Zenodo repository](https://zenodo.org/records/18727698).

This Zenodo repository contains all the processed and raw data used in the study, organized into subfolders for clarity:

- `Sessions_from_ChargePlaceScotland/` – Standardized Excel files prepared for preprocessing.  
- `glasgow_datasets/` – Raw datasets specific to the Glasgow region (case study).  
- `infos_cpids/` – Metadata linking charge point identifiers (CPIDs) to technical specifications.  
- `Master_file_scotland_dataset/` – Core longitudinal dataset for Scotland covering 2022–2025.  
- `Meteo_dataset/` – Weather-related covariates used in the models.  
- `shapefiles_for_maps/` – Spatial boundaries for map visualizations and geographic indexing.

All datasets have been curated and structured to facilitate reproducibility and further analysis.
To run the code, please **download the dataset folders** from Zenodo and place them into a local folder named `datasets/` in the project root.  

### Model
Contains R scripts for model implementation and comparison:
- `Distribution by Neighborhood.R` – Spatial distribution analysis.
- `INLA_code.R` – Main INLA model implementation.
- `Local_models_vs_inla.R` – Comparison of site-specific models versus the INLA model.
- `Weather Dataset Preparatio.R` – Scripts preparing weather covariates.

### Preprocessing
Contains Python scripts and notebooks to clean, standardize, and preprocess raw data:
- `CODE_preprocessing.py` – Python script for automated preprocessing steps.
- `Final_preprocessing_EDA.ipynb` – Notebook with full preprocessing and EDA.
- `Preparation_2025_2024.ipynb` – Notebook for data preparation for years 2024–2025.
- `preparation_Nov23.ipynb` – Preprocessing notebook for November 2023 datasets.
- `set_column_names.py` – Helper script to standardize column names.
- `standarized_columns` – Reference file for standardized column names used in preprocessing.
### Figures
Contains figures generated during analysis and for manuscript preparation.
