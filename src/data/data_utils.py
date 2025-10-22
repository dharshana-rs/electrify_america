import pandas as pd
import numpy as np

STATE_ABBREV = {
    'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO',
    'Connecticut':'CT','Delaware':'DE','District of Columbia':'DC','Florida':'FL','Georgia':'GA',
    'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS',
    'Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA',
    'Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT',
    'Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM',
    'New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK',
    'Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD',
    'Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA',
    'West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'
}

def add_time_parts(df, dt_col) :
    out = df.copy()
    out[dt_col] = pd.to_datetime(out[dt_col], errors="coerce", utc=True).dt.tz_convert(None)
    out["Year"]  = out[dt_col].dt.year
    out["Month"] = out[dt_col].dt.month
    out["Day"]   = out[dt_col].dt.day
    out["Hour"]  = out[dt_col].dt.hour
    out["month_label"] = out[dt_col].dt.to_period("M").astype(str)  
    return out

def month_label_nice(year, month):
    #d = pd.to_datetime(dict(year=year, month=month)
    d = pd.to_datetime(dict(year=year, month=month, day=1), errors="coerce")
    return d.dt.strftime("%b, %Y")

def safe_numeric(df, cols) :
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out

def normalize_state_name(s):
    return s.astype(str).str.strip()

def abbr_from_state(state_name):
    return state_name.map(STATE_ABBREV)


