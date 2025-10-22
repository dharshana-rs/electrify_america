from pathlib import Path
from dataclasses import dataclass

@dataclass
class Paths:
    # base dirs
    data_dir: Path
    raw: Path
    external: Path
    interim: Path
    processed: Path

    # input file names 
    evwatts_sessions_csv: Path
    afs_stations_csv: Path
    afdc_regs_csv: Path
    fips_ref_csv: Path

    # interim file names 
    #ev_vehicle_df: Path
    #ev_all_sessions: Path

    # outputs
    stations_clean_csv: Path
    sessions_clean_csv: Path
    state_month_agg_csv: Path
    station_month_merged_csv: Path

def build_paths(base: str = "data"):
    base_dir = Path(base)
    raw = base_dir / "raw"
    external = base_dir / "external"
    interim = base_dir / "interim"
    processed = base_dir / "processed"

    raw.mkdir(parents=True, exist_ok=True)
    external.mkdir(parents=True, exist_ok=True)
    interim.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)

    return Paths(
        data_dir=base_dir,
        raw=raw,
        external=external,
        interim=interim,
        processed=processed,
        evwatts_sessions_csv=raw / "evsessions.csv",  
        afs_stations_csv=raw / "Alternative_Fueling_Stations.csv",
        afdc_regs_csv=raw / "afdc_vehicle_registrations.csv",
        fips_ref_csv=external / "State__County_and_City_FIPS_Reference_Table.csv",
        stations_clean_csv=interim / "afs_stations_clean.csv",
        sessions_clean_csv=interim / "evsessions_clean.csv",
        state_month_agg_csv=processed / "state_month_agg.csv",
        station_month_merged_csv=processed / "processed_ev_demand.csv",
    )


#print( build_paths() )