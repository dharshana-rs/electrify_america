import os
import pandas as pd
import requests
from typing import Optional

CENSUS_BASE = "https://api.census.gov/data/2022/acs/acs5"

def fetch_state_population_income(api_key = None):
    params = {
        "get": "NAME,B01003_001E,B19013_001E",
        "for": "state:*"
    }
    if api_key:
        params["key"] = api_key

    r = requests.get(CENSUS_BASE, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    cols = data[0]
    rows = data[1:]
    df = pd.DataFrame(rows, columns=cols)
    df.rename(columns={
        "NAME": "STATE_NAME",
        "B01003_001E": "POPULATION",
        "B19013_001E": "MEDIAN_INCOME",
        "state": "STATE_FIPS"
    }, inplace=True)

    df["POPULATION"] = pd.to_numeric(df["POPULATION"], errors="coerce")
    df["MEDIAN_INCOME"] = pd.to_numeric(df["MEDIAN_INCOME"], errors="coerce")
    return df


#print( fetch_state_population_income("dferr2e453434fefegerfret43fref") )