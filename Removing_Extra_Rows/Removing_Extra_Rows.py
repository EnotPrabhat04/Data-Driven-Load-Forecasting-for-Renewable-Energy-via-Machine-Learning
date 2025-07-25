#usage python file_name.py /path/to/your/GHI_MW_Complete.xlsx


import sys
from pathlib import Path

import pandas as pd


def filter_time_range(input_path: Path):
    # 1) Read
    df = pd.read_excel(input_path)

    # 2) Ensure time_ist is datetime
    df['time_ist'] = pd.to_datetime(df['time_ist'])

    # 3) Build mask for times between 06:30 and 17:30
    start_time = pd.to_datetime('06:30:00').time()
    end_time = pd.to_datetime('17:30:00').time()
    mask = df['time_ist'].dt.time.between(start_time, end_time)

    # 4) Filter
    filtered = df.loc[mask].copy()

    # 5) Save to new Excel in same folder
    out_path = input_path.parent / 'GHI_MW_Complete_final.xlsx'
    filtered.to_excel(out_path, index=False)
    print(f"✅ Filtered {len(filtered)} rows saved to:\n   {out_path}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python filter_time_range.py /path/to/your/input.xlsx")
        sys.exit(1)
    inp = Path(sys.argv[1])
    if not inp.exists():
        print(f"❌ File not found: {inp}")
        sys.exit(1)
    filter_time_range(inp)
