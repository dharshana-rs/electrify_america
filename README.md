# Forecasting Demand for Electric Vehicle Charging Stations  
### Team 23 — Dharshana Somasunderam, Zara Masood, and Duy Ho  

---

## Overview  
In the United States, the increase usage of electric vehicles (EVs) is placing new demands on public charging infrastructure.  
This project's goal is to **forecast charging demand** and **identify regional infrastructure gaps** by combining session-level EV charging data, station-level infrastructure data, and demographic factors.  

We apply both **supervised** and **unsupervised** learning methods to analyze how factors such as time, pricing, facility type, and socioeconomic factors influence energy usage and station demand.  
The ultimate goal is to provide insights that help policymakers, energy companies, and charging station companies make data oriented infrastructure decisions.

---

## Project Objectives  
1. **Forecast Charging Demand (Supervised Learning)**  
   - Predict session-level energy consumption and daily demand using regression and classification models.  
   - Evaluate models including Linear Regression, Random Forest, and Gradient Boosting.  

2. **Cluster EV Stations and Regions (Unsupervised Learning)**  
   - Group regions by infrastructure characteristics and usage intensity.  
   - Apply and evaluate methods such as K-Means, DBSCAN, and Hierarchical Clustering.  

3. **Merge and Enrich Data Sources**  
   - Combine multiple government datasets (EV WATTS, AFS, AFDC, Census, FIPS).  
   - Integrate demographic and socioeconomic features for enhanced insights.
