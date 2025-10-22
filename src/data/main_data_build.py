import os
import argparse
from dotenv import load_dotenv
from pathlib import Path

from data_config import build_paths
from merge_pipeline import load_clean_afs, load_clean_evwatts, load_clean_afdc_regs, merge_station_month

def parse_args():
    p = argparse.ArgumentParser(
        description="Build merged datasets for EV demand modeling."
    )
    p.add_argument("--data-dir", default="data", help="Base data directory")
    p.add_argument("--evwatts", default=None, help="Override EV WATTS CSV path")
    p.add_argument("--afs", default=None, help="Override AFS stations CSV path")
    p.add_argument("--regs", default=None, help="Override AFDC registrations CSV path")
    p.add_argument("--fips", default=None, help="Override FIPS reference CSV path (optional)")
    return p.parse_args()

def main():
    print("Data building started...")
    load_dotenv()
    args = parse_args()
    paths = build_paths(args.data_dir)

    if args.evwatts: paths.evwatts_sessions_csv = Path(args.evwatts)
    if args.afs:     paths.afs_stations_csv    = Path(args.afs)
    if args.regs:    paths.afdc_regs_csv       = Path(args.regs)
    if args.fips:    paths.fips_ref_csv        = Path(args.fips)

    print("Loading Alternative Fueling Stations...")
    afs = load_clean_afs(paths)
    afs.to_csv(paths.stations_clean_csv, index=False)
    print(f"File Saved {paths.stations_clean_csv}")

    print("Loading EV WATTS sessions...")
    ev = load_clean_evwatts(paths)
    ev.to_csv(paths.sessions_clean_csv, index=False)
    print(f"File Saved {paths.sessions_clean_csv}")

    print("Loading AFDC vehicle registrations...")
    regs = load_clean_afdc_regs(paths)

    print("Merging to state-month layer with demographics...")
    api_key = os.getenv("CENSUS_API_KEY")
    merged = merge_station_month(ev, afs, regs, api_key=api_key)
    merged.to_csv(paths.state_month_agg_csv, index=False)
    print(f"File Saved {paths.state_month_agg_csv}")

    print("Data build complete.")

if __name__ == "__main__":
    main()