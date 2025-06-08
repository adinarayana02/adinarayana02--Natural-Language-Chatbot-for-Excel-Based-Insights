# utils.py - Data cleaning and type inference

import pandas as pd
import re

def clean_column_name(col_name):
    # Lowercase, strip, and replace spaces/special chars for easier access
    cleaned = col_name.strip().lower()
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned

def preprocess_dataframe(input_df):
    df = input_df.copy()
    df.columns = [clean_column_name(c) for c in df.columns]
    for col in df.columns:
        numeric = pd.to_numeric(df[col], errors='coerce')
        if numeric.notna().sum() / len(df) > 0.5:
            df[col] = numeric
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)
            continue
        dt = pd.to_datetime(df[col], errors='coerce')
        if dt.notna().sum() / len(df) > 0.5:
            df[col] = dt
            if df[col].isnull().any():
                df[col].fillna(method='ffill', inplace=True)
            continue
        bool_like = df[col].astype(str).str.lower().isin(["true", "false", "yes", "no", "1", "0"])
        if bool_like.sum() / len(df) > 0.5:
            df[col] = df[col].astype(str).str.lower().map({
                "true": True, "yes": True, "1": True,
                "false": False, "no": False, "0": False
            })
            if df[col].isnull().any():
                df[col].fillna(False, inplace=True)
            continue
        if df[col].isnull().any():
            df[col] = df[col].astype(str).fillna("Unknown")
    return df

def get_column_data_types(df):
    out = {"numerical_type": [], "categorical_type": [], "boolean_type": [], "datetime_type": []}
    for col in df.columns:
        non_null = df[col].dropna()
        if pd.api.types.is_bool_dtype(non_null):
            out["boolean_type"].append(col)
        elif pd.api.types.is_numeric_dtype(non_null):
            out["numerical_type"].append(col)
        elif pd.api.types.is_datetime64_any_dtype(non_null):
            out["datetime_type"].append(col)
        else:
            out["categorical_type"].append(col)
    return out