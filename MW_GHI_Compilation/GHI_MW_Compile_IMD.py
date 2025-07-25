
import os
import pandas as pd

#Configuration
GHI_FILE     = r"C:\Users\Prabhat\PycharmProjects\PythonProject\RE_Forecast_Interns\IMD_Trial\Final_ready_file\GHI_Compilation_15minSplittedData.xlsx"
MW_FILE      = r"C:\Users\Prabhat\PycharmProjects\PythonProject\RE_Forecast_Interns\Compiled_Actual data(till 18 23 MARCH 25)1 WEEKS MISSING.xlsx"
MAPPING_FILE = r"C:\Users\Prabhat\PycharmProjects\PythonProject\RE_Forecast_Interns\IMD_mapping.xlsx"

#Output will be next to GHI_FILE, named *_merged.xlsx
BASE, EXT = os.path.splitext(GHI_FILE)
OUTPUT_FILE = f"{BASE}_GHI_MW_merged{EXT}"

def load_mapping(path):
    """Read mapping file and return dict: SCADA_name → IMD_name."""
    df = pd.read_excel(path, dtype=str)
    df = df.dropna(how="all")  # drop empty rows
    # assume first two columns are the mapping
    scada_col, imd_col = df.columns[0], df.columns[1]
    mapping = dict(zip(df[scada_col].str.strip(), df[imd_col].str.strip()))
    return mapping

def load_ghi(path, mapping):
    """Load GHI, parse time, rename stations via mapping, suffix '_GHI'."""
    df = pd.read_excel(path, dtype=str)
    # parse timestamp
    df["time_ist"] = pd.to_datetime(df["time_ist"], format="%Y-%m-%d %H:%M:%S")
    # rename mapped columns
    df.rename(columns=mapping, inplace=True)
    # suffix all station columns
    cols = [c for c in df.columns if c != "time_ist"]
    df.rename(columns={c: f"{c}_GHI" for c in cols}, inplace=True)
    return df

def load_mw(path, mapping):
    """Load MW from first sheet (header row=0), parse time, rename, suffix '_MW'."""
    # read sheet 1; assumes header row contains station names, first column is timestamp
    df = pd.read_excel(path, sheet_name=0, dtype=str)
    # parse timestamp
    ts_col = df.columns[0]
    df.rename(columns={ts_col: "time_ist"}, inplace=True)
    df["time_ist"] = pd.to_datetime(df["time_ist"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    df = df.dropna(subset=["time_ist"])
    # strip station names
    stat_cols = [c for c in df.columns if c != "time_ist"]
    df.rename(columns={c: c.strip() for c in stat_cols}, inplace=True)
    # rename mapped columns
    df.rename(columns=mapping, inplace=True)
    # suffix all station cols
    cols2 = [c for c in df.columns if c != "time_ist"]
    df.rename(columns={c: f"{c}_MW" for c in cols2}, inplace=True)
    return df

def main():
    #load mapping
    mapping = load_mapping(MAPPING_FILE)

    #load GHI & MW
    ghi_df = load_ghi(GHI_FILE, mapping)
    mw_df  = load_mw (MW_FILE, mapping)

    #merge on the timestamps present in both
    merged = pd.merge(
        ghi_df, mw_df,
        on="time_ist",
        how="inner",
        sort=True
    )

    #reorder: time_ist, then pairs of _GHI & _MW for each station
    #find unique station base names:
    bases = sorted({
        col.rsplit("_",1)[0]
        for col in merged.columns
        if col != "time_ist"
    })
    cols = ["time_ist"]
    for b in bases:
        ghi_col = f"{b}_GHI"
        mw_col  = f"{b}_MW"
        if ghi_col in merged.columns and mw_col in merged.columns:
            cols += [ghi_col, mw_col]
    merged = merged[cols]

    #save
    merged.to_excel(OUTPUT_FILE, index=False)
    print(f"Merged file written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
