import pandas as pd
import numpy as np
import os
import logging
import argparse
from datetime import timedelta
from tqdm import tqdm


# Logging
logging.basicConfig(
    filename='GHI_Compilation_HMV_FInal_5_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# Arguments
parser = argparse.ArgumentParser(
    description='GHI Data Extraction with Time‑of‑Day Linear Interpolation'
)
parser.add_argument('--start_date', required=True, type=str,
                    help='YYYY-MM-DD start date')
parser.add_argument('--end_date',   required=True, type=str,
                    help='YYYY-MM-DD end date')
args = parser.parse_args()

start_date = pd.to_datetime(args.start_date)
end_date   = pd.to_datetime(args.end_date)

# Base directory path
base_dir = "C:/MOSDAC 2024-25 Data"

# List of stations whose GHI data is to be extracted (Needed to be Hardcoded)
stations_IMD = [
    "ACME_Chittorgarh", "Azure34", "ARERJL", "ASE4PL", "ASEJ2L",
    "Azure_Adani", "Azure_Mapple", "Azure_Power41",
    "Clean_Solar_Power_Jodhpur", "CSP_Saurya_Urja", "Mahindra_Bhadla",
    "Renew_Adani", "SB_Energy_Saurya_Urja", "SB_Energy_Six",
    "Tata_Power_Bhadla", "Adani_Hybrid_4_Solar", "NTPC_Nidan",
    "ABC_Renewables", "ACME_Heergarh", "Mega_Solar_Urja",
    "Avaada_Sunrays", "NTPC_Kolayat", "NTPC_Nokhra",
    "Adani_Hybrid_1_Solar", "Adani_Hybrid_2_Solar",
    "Adani_Hybrid_3_Solar", "ASEJOPL_Solar", "NTPC_Devikot_",
    "Eden", "Renew_Jharkhand_3", "Renew_Sun_Bright",
    "Renew_Solar_Urja", "Renew_Sun_Wave", "Avaada_Rajhans",
    "Avaada_Sunce", "Avaada_Sustainable", "Ayana", "Azure43",
    "Renew_Solar_Ravi_Bikaner", "Renew_Power_Bikaner",
    "SBSR_Power_Bikaner", "Thar_Surya_1", "Tata_Green_Energy_Bikaner"
]

date_range     = pd.date_range(start=start_date, end=end_date, freq='D')
daily_data_map = {}
time_freq      = None

# STEP 1: READ AND STORE REAL DAYS
for date in tqdm(date_range, desc="Reading Files"):
    folder    = date.strftime('%Y%m%d')
    file_path = os.path.join(
        base_dir, folder, 'imdData', folder + '00', f'GHI_{folder}.csv'
    )

    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df['time'] = pd.to_datetime(df['time'],
                                        format='%Y%m%d%H',
                                        utc=True)
            # select 01:00–12:00 UTC → 06:30–17:30 IST
            start_utc = pd.Timestamp(date.strftime('%Y-%m-%d') + ' 01:00',
                                     tz='UTC')
            end_utc   = start_utc + timedelta(hours=11)
            df = df[(df.time >= start_utc) & (df.time <= end_utc)]
            df = df[df.station.isin(stations_IMD)]
            df['time_ist'] = (df.time
                              .dt.tz_convert('Asia/Kolkata')
                              .dt.tz_localize(None))
            pivot = (
                df.pivot_table(index='time_ist',
                               columns='station',
                               values='GHI')
                  .reindex(columns=stations_IMD)
            )
            if time_freq is None and len(pivot) > 1:
                time_freq = pd.infer_freq(pivot.index) or '60min'

            daily_data_map[date] = pivot
            logging.info(f"Loaded real data for {date.date()}")
        except Exception as e:
            logging.error(f"Error reading {date.date()}: {e}")
            daily_data_map[date] = None
    else:
        logging.warning(f"File missing for {date.date()}")
        daily_data_map[date] = None

# STEP 2: REINDEX DAYS ONTO A UNIFORM INDEX
all_days = []
for date in tqdm(date_range, desc="Reindexing Days"):
    idx = pd.date_range(
        start=date + timedelta(hours=6, minutes=30),
        end  =date + timedelta(hours=17, minutes=30),
        freq =time_freq or '60min'
    )
    df = daily_data_map[date]
    if df is not None:
        df = df.reindex(idx)
    else:
        df = pd.DataFrame(index=idx, columns=stations_IMD, dtype=float)
    df.index.name = 'time_ist'
    all_days.append(df)

# concatenate into one continuous series
full_df = pd.concat(all_days)
full_df = full_df[~full_df.index.duplicated()]
full_df = full_df.sort_index()


# STEP 3: TIME‑OF‑DAY LINEAR INTERPOLATION
# directly get the unique time‑of‑day values from the index
times_of_day = pd.Index(full_df.index.time).unique()

for tod in times_of_day:
    mask     = full_df.index.time == tod
    slice_df = full_df.loc[mask]
    interp   = slice_df.interpolate(
        method='time',
        axis=0,
        limit_direction='both'
    )
    full_df.loc[mask] = interp

# fill any remaining NaNs at the very start/end
full_df = full_df.ffill().bfill()


# STEP 4: Export and save it to a new Excel file
output_path = "GHI_Compilation_HMV_Final_5.xlsx"
full_df.to_excel(output_path)
logging.info(f" Final Excel saved to {output_path}")
print(f" Completed — saved interpolated GHI to {output_path}")
