

#Usage:python Split_into_15Min.py path/to/your/input.xlsx


import sys
import os
import pandas as pd

def split_to_15min(input_path: str):
    #CONFIGURE YOUR DAILY WINDOW HERE
    start_time_str = "06:30:00"   # 6:30 AM
    end_time_str   = "19:30:00"   # 7:30 PM

    #derive output filename in same directory
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_15min{ext}"

    #read all columns as strings
    df = pd.read_excel(input_path, dtype=str)

    #pick your timestamp column
    ts_col = "time_ist"
    if ts_col not in df.columns:
        ts_col = df.columns[0]
        print(f"'time_ist' not found—using '{ts_col}' instead.")

    #parse to datetime (strict format), coerce bad → NaT
    df[ts_col] = pd.to_datetime(
        df[ts_col],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )

    #drop any unparseable rows
    bad = df[df[ts_col].isna()]
    if not bad.empty:
        print(f" Dropping {len(bad)} rows with invalid timestamps.")
        df = df.dropna(subset=[ts_col])

    #filter to your daily window
    st = pd.to_datetime(start_time_str, format="%H:%M:%S").time()
    et = pd.to_datetime(end_time_str,   format="%H:%M:%S").time()
    df = df[(df[ts_col].dt.time >= st) & (df[ts_col].dt.time <= et)]

    #sort by timestamp
    df = df.sort_values(ts_col).reset_index(drop=True)

    #identify data columns to interpolate
    data_cols = [c for c in df.columns if c != ts_col]
    output_rows = []

    #for each adjacent pair, interpolate into 4×15 min steps
    for i in range(len(df) - 1):
        a = df.iloc[i]
        b = df.iloc[i + 1]

        t0, t1 = a[ts_col], b[ts_col]
        delta = (t1 - t0) / 4

        v0 = a[data_cols].astype(float)
        v1 = b[data_cols].astype(float)
        step = (v1 - v0) / 4

        for j in range(4):  # 0,15,30,45 min
            t_new = t0 + j * delta
            vals  = (v0 + step * j).to_dict()
            output_rows.append({ts_col: t_new, **vals})

    # append the very last original row
    last = df.iloc[-1]
    output_rows.append({ts_col: last[ts_col], **last[data_cols].astype(float).to_dict()})

    #7 write output
    out_df = pd.DataFrame(output_rows)
    out_df.to_excel(output_path, index=False)
    print(f" Done 15‑min split saved to:\n   {output_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python Split_into_15Min.py <input_excel_path>")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"Error: file not found → {path}")
        sys.exit(1)

    split_to_15min(path)

if __name__ == "__main__":
    main()
