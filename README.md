# Electrify America: Forecasting Electric Vehicle Charging Demand

## Team 23 — Milestone II Final Project

    Contributors: Dharshana Somasunderam (DS), Zara Masood (ZM), Duy Ho (DH)
    Course: SIADS 696 012 FA 2025 - Milestone II
    Institution: University of Michigan, SIADS
    Term: Fall 2025



## Project Overview 

The Electrify America project aims to forecast electric vehicle (EV) charging demand and identify regional infrastructure gaps across the United States.
Using a combination of supervised and unsupervised learning, our goal is to understand when and where EV charging demand will increase and how effectively the existing infrastructure meets that demand.

We integrate session-level behavioral charging data, station-level infrastructure, and regional socioeconomic factors into a single dataframe to guide policy decisions, utility planning, and infrastructure investments.



## Problem Statement

As EV ownership grows rapidly, the demand for electricity and public charging stations is surging unevenly across the U.S.
Poorly distributed infrastructure risks creating accessibility issues and bottlenecks in sustainable transportation.
Our project addresses the question:

#### Where and when will EV charging demand increase, and how well does the current infrastructure meet that demand?

## Motivation

We are motivated to explore this project due to the growth of decarbonization policies, and a focus on environmentally friendly transportation. We noticed that there are several analyses focusing mainly on vehicle registration or station availability, but only few study about charging behavior and infrastructure characteristics at a granular, station-level scale. To address this gap, our team took this as an opportunity to combine multiple national datasets which we found. The datasets we decided to combine are EV WATTS, Alternative Fueling Stations, AFDC Vehicle Registration, and U.S. Census data to build a strong view of electric vehicle’s charging demand.


## Methods Summary

### Supervised Learning

We modeled EV charging demand (demand_score) using:

	•	Ridge Regression (regularized linear baseline)
	•	Random Forest Regressor
	•	Gradient Boosting Regressor
    

Each model predicts energy consumption and average session counts using temporal, station, and regional features.

### Unsupervised Learning

We performed clustering to identify:

	•	Station archetypes (micro-level patterns using K-Means and DBSCAN)
	•	Regional investment tiers (macro-level patterns across U.S. states)

Evaluation metrics: Silhouette Score, Davies–Bouldin Index, Noise Ratio (DBSCAN).

## Data Sources

All datasets are open-source and government-maintained, spanning 2019–2023.

| Dataset | Description | Source |
| -------- | -------- | -------- |
| EV WATTS Public Dataset | 300K+ session-level charging records | U.S. DOE – EV WATTS |
| Alternative Fueling Stations (AFS) | Station-level metadata for 300K+ facilities | U.S. DOT – BTS |
| AFDC Vehicle Registration Data | Annual EV/Hybrid registration counts (2018–2023) | DOE AFDC |
| U.S. Census ACS Data | Annual EV/Hybrid registration counts (2018–2023) | DOE AFDC |
| State–County FIPS Reference | Population and median income by state/county | U.S. Census API |
| Alternative Fueling Stations (AFS) | FIPS-based geographic join table | U.S. DOT FIPS Reference |


## Feature Engineering

We combined and cleaned raw data through:

	1.	Standardization: Date/time formatting, unit normalization.
	2.	Geographic Merging: Using FIPS codes for consistent joins.
	3.	Missing Data Handling: Mode/missing imputation and census-based filling.
	4.	Feature Encoding: One-hot encoding categorical variables, min–max normalization for numeric data.
	5.	Derived Features:

	    •	total_ports = ev_level2_evse_num + ev_dc_fast_num
	    •	charging_efficiency = energy_kwh / charge_duration
	    •	urbanization_index = population / number_of_stations



Final dataset:

	•	~110,000 records
	•	25–30 engineered features
	•	Coverage: 2019–2023
	•	Level: Station–Month–State

## Model Evaluation

Supervised Models

| Model | Mean RMSE | Mean MAE | Mean R² |
| -------- | -------- | -------- | -------- |
| Linear Regression | 262.96 | 117.55 | 0.78 |
| Random Forest | 20.33 | 0.47 | 0.999 |
| Gradient Boosting | 12.97 | 1.73 | 0.999 |


Unsupervised Clustering

| Model | Optimal K | Silhouette Score | DBSCAN | Interpretation |
| -------- | -------- | -------- | -------- | -------- |
| Station K-Means | 4 | ~0.85 | — | Fast-hub, workplace, community, mixed-use archetypes |
| Regional K-Means | 3 | ~0.80 | — | Mature, High Concentration, Slow markets |
| Station DBSCAN | —| — | 323 clusters + ~3.3% noise | Validates dense vs. sparse infrastructure patterns |


## Visual Insights

	•	EV Charging Demand Heatmap: Predicted demand intensity across U.S. stations.
	•	Investment Priority Map: Clusters states into Mature, High-Concentration, and Slow-Market segments.
	•	SHAP Plot: Highlights key features driving demand prediction.
	•	Learning Curve: Demonstrates model generalization over training size.


## Repository Structure

    .
    ├── data/
    │   ├── raw/                # Original datasets (EV WATTS, AFS, Census, etc.)
    │   ├── processed/          # Cleaned & merged datasets
    ├── notebooks/
    │   ├── Data_Merge.ipynb
    │   ├── SL.ipynb            # Supervised learning notebook
    │   ├── UnSupervised_Learning.ipynb
    ├── results/
    │   ├── figures/            # Visualizations and charts
    │   ├── models/             # Saved model files (if any)
    ├── report/
    │   ├── Milestone_II_Final_Report.pdf
    │   ├── README.md
    └── LICENSE




## License

This project uses open-source data and is released under the MIT License.
All datasets are publicly available via U.S. government open data portals.

## Contact

For questions or collaboration:

	•	Team: Dharshana Somasunderam (DS), Zara Masood (ZM), Duy Ho (DH)
	•	Email: sdharsha@umich.edu, zarama@umich.edu, duyho@umich.edu
	•	GitHub Repository: https://github.com/dharshana-rs/electrify_america

## Key Insights:

	•	Ensemble models outperform linear ones due to non-linear feature relationships.
	•	Population and number of ports were the most impactful predictors.

