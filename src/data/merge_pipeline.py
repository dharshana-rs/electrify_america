import os
import pandas as pd
import numpy as np
from typing import Tuple
from .data_config import Paths
from .data_utils import ( add_time_parts, safe_numeric, normalize_state_name, abbr_from_state )
from .census_api import fetch_state_population_income
#from data_utils import add_time_parts, month_label_nice, abbr_from_state, normalize_state_name, safe_numeric

def load_clean_afs(paths):
    df = pd.read_csv(paths.afs_stations_csv, low_memory=False)
    keep = {
        "id":"id","station_name":"station_name","city":"city","state":"state",
        "street_address":"street_address","zip":"zip","latitude":"latitude","longitude":"longitude",
        "ev_connector_types":"ev_connector_types","ev_level1_evse_num":"ev_level1_evse_num",
        "ev_level2_evse_num":"ev_level2_evse_num","ev_dc_fast_num":"ev_dc_fast_num",
        "ev_pricing":"ev_pricing","access_days_time":"access_days_time","facility_type":"facility_type",
        "ev_network":"ev_network","date_last_confirmed":"date_last_confirmed"
    }
    
    df.columns = [c.strip().lower() for c in df.columns]
    df = df[[c for c in keep.keys() if c in df.columns]].rename(columns=keep)
    
    num_cols = ["ev_level1_evse_num","ev_level2_evse_num","ev_dc_fast_num","latitude","longitude"]
    df = safe_numeric(df, num_cols)
    df["state"] = df["state"].astype(str).str.upper()
    df["facility_type"] = df["facility_type"].fillna("UNKNOWN")
    df["ev_pricing"] = df["ev_pricing"].fillna("UNSPECIFIED")
    df = add_time_parts(df, "date_last_confirmed")
    return df

def load_clean_evwatts(paths):
    df = pd.read_csv(paths.evwatts_sessions_csv, low_memory=False)
    df.columns = [c.strip().lower() for c in df.columns]
    rename_map = {
        "session_id":"session_id","evse_id":"evse_id","start_datetime":"start_datetime",
        "end_datetime":"end_datetime","total_duration":"total_duration",
        "charge_duration":"charge_duration","energy_kwh":"energy_kwh",
        "connector_type":"connector_type","power_kw":"power_kw",
        "charge_level":"charge_level","pricing":"pricing","region":"region","state":"state",
        "metro_area":"metro_area","venue":"venue","num_ports":"num_ports"
    }
    
    keep_cols = {k:v for k,v in rename_map.items() if k in df.columns}
    df = df[list(keep_cols.keys())].rename(columns=keep_cols)

    numeric_cols = ["total_duration","charge_duration","energy_kwh","power_kw","num_ports"]
    df = safe_numeric(df, [c for c in numeric_cols if c in df.columns])
    #df["state"] = df["state"].astype(str).str.upper()
    df["state"] = df["state"].astype(str).str.upper() if "state" in df.columns else np.nan
    df = add_time_parts(df, "start_datetime")
    
    #if "energy_kwh" in df.columns and "charge_duration" in df.columns:
    #    df["demand_score"] = df["energy_kwh"] * df["charge_duration"]
    #return df

    if "energy_kwh" in df.columns and "charge_duration" in df.columns:
        df["demand_score"] = df["energy_kwh"].fillna(0) + 0.1 * df["charge_duration"].fillna(0)
    return df

def load_clean_afdc_regs(paths):
    df = pd.read_csv(paths.afdc_regs_csv, low_memory=False)
    df.columns = [c.strip().lower() for c in df.columns]
    rename = {
        "state":"state_name","year":"year",
        "electric_vehicle_reg_count":"electric_vehicle_reg_count",
        "plug_in_hybrid_vehicle_reg_count":"plug_in_hybrid_vehicle_reg_count",
        "hybrid_electric_reg_count":"hybrid_electric_reg_count"
    }
    keep = [c for c in rename.keys() if c in df.columns]
    df = df[keep].rename(columns=rename)
    df["state_name"] = normalize_state_name(df["state_name"])
    df["state"] = abbr_from_state(df["state_name"])
    for c in ["electric_vehicle_reg_count","plug_in_hybrid_vehicle_reg_count","hybrid_electric_reg_count","year"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def attach_census(df_state: pd.DataFrame, api_key: str | None) -> pd.DataFrame:
    census = fetch_state_population_income(api_key)
    census["STATE_NAME"] = normalize_state_name(census["STATE_NAME"])
    census["state"] = abbr_from_state(census["STATE_NAME"])
    census = census[["state","STATE_NAME","POPULATION","MEDIAN_INCOME"]]
    out = df_state.merge(census, on="state", how="left")
    return out



def aggregate_state_month(ev):
    cols_present = [c for c in ["state","Year","Month","energy_kwh","charge_duration","total_duration","demand_score"] if c in ev.columns]
    g = ev[cols_present].groupby(["state","Year","Month"], as_index=False).agg(
        energy_kwh_sum=("energy_kwh","sum"),
        charge_duration_sum=("charge_duration","sum"),
        total_duration_sum=("total_duration","sum"),
        sessions=("state","count"),
        demand_score_sum=("demand_score","sum"),
    )
    g["month_label"] = g.apply(lambda r: f"{int(r['Year'])}-{int(r['Month']):02d}", axis=1)
    return g

def merge_station_month(ev, afs, regs, api_key = None):
    # EV sessions monthly at (state, Year, Month)
    state_month = aggregate_state_month(ev)

    # station counts by state (from AFS)
    if {"state","ev_level2_evse_num","ev_dc_fast_num"}.issubset(afs.columns):
        station_counts = (
            afs.groupby("state", as_index=False)
               .agg(num_stations=("id","count"),
                    total_l2=("ev_level2_evse_num","sum"),
                    total_dcfc=("ev_dc_fast_num","sum"))
        )
    else:
        station_counts = afs.groupby("state", as_index=False).agg(num_stations=("id","count"))

    # vehicle registrations (state-year)
    regs_sm = regs.groupby(["state","year"], as_index=False).agg(
        ev_regs=("electric_vehicle_reg_count","sum"),
        phev_regs=("plug_in_hybrid_vehicle_reg_count","sum"),
        hev_regs=("hybrid_electric_reg_count","sum"),
    )

    # join state-month with nearest year registrations (inner on state then nearest year)
    merged = state_month.merge(regs_sm, left_on=["state","Year"], right_on=["state","year"], how="left")
    merged.drop(columns=["year"], inplace=True, errors="ignore")

    # add station supply
    merged = merged.merge(station_counts, on="state", how="left")

    # add census demographics
    merged = attach_census(merged, api_key)

    # derived ratios
    merged["adoption_ratio"] = merged["ev_regs"] / merged["POPULATION"]
    merged["infra_balance_ratio"] = merged["num_stations"] / merged["ev_regs"]
    return merged