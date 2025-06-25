import os
import pandas as pd
from glob import glob

def dedup_columns(cols):
    """Add suffixes to duplicate columns to make them unique."""
    seen = {}
    result = []
    for col in cols:
        if col not in seen:
            seen[col] = 0
            result.append(col)
        else:
            seen[col] += 1
            new_col = f"{col}.{seen[col]}"
            while new_col in seen:
                seen[col] += 1
                new_col = f"{col}.{seen[col]}"
            seen[new_col] = 0
            result.append(new_col)
    return result

def clean_and_merge_year_tables(year, input_dir="mlb_yearly_data", output_dir="mlb_cleaned"):
    os.makedirs(output_dir, exist_ok=True)
    pattern = os.path.join(input_dir, f"mlb_{year}_table_*.csv")
    files = sorted(glob(pattern))

    cleaned_dfs = []

    for file in files:
        df = pd.read_csv(file)

        # Drop rows that look like headers or junk
        df = df[~df.iloc[:, 0].astype(str).str.contains("Statistic|N.L. History|Team", na=False)]

        # Drop empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')

        # Deduplicate column names
        df.columns = dedup_columns(df.columns)

        # Rename confusing team column to 'Team' if present
        if 'Team..|..Roster' in df.columns:
            df.rename(columns={'Team..|..Roster': 'Team'}, inplace=True)

        # Remove duplicate columns, keep first occurrence
        df = df.loc[:, ~df.columns.duplicated()]

        if not df.empty:
            cleaned_dfs.append(df)

    if cleaned_dfs:
        merged = pd.concat(cleaned_dfs, ignore_index=True)
        merged.to_csv(os.path.join(output_dir, f"mlb_{year}_cleaned.csv"), index=False)
        print(f"Cleaned and saved: mlb_{year}_cleaned.csv")
    else:
        print(f"No valid tables found for {year}.")

def clean_all_years(input_dir="mlb_yearly_data", output_dir="mlb_cleaned"):
    all_raw_tables = glob(os.path.join(input_dir, "mlb_*_table_*.csv"))
    years = sorted(set(os.path.basename(f).split("_")[1] for f in all_raw_tables))

    for year in years:
        clean_and_merge_year_tables(year, input_dir, output_dir)

if __name__ == "__main__":
    clean_all_years()
