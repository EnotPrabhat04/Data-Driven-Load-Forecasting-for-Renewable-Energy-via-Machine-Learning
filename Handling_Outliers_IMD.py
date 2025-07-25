import pandas as pd
import logging
import os

#Path to your original Excel file
input_path = r"C:\Users\Prabhat\PycharmProjects\PythonProject\RE_Forecast_Interns\IMD_Trial\Final_ready_file\GHI_MW_Compilation_IMD.xlsx"

#Drive output & log paths to live alongside the input file
base_dir = os.path.dirname(input_path)
stem     = os.path.splitext(os.path.basename(input_path))[0]

output_path = os.path.join(base_dir, f"{stem}_with_Outliers.xlsx")
log_path    = os.path.join(base_dir, f"{stem}_bounds_log.txt")

#Prepare the log file (overwrite if already there)
if os.path.exists(log_path):
    os.remove(log_path)

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.info(" Outlier bounds log started ")

#Read in your data (assumes 'time_ist' is the datetime column)
df = pd.read_excel(
    input_path,
    sheet_name="Sheet1",
    parse_dates=["time_ist"]
)

#Identify all numeric columns (i.e. your GHI & MW station data)
numeric_cols = df.select_dtypes(include="number").columns

#Cap each column and log its computed bounds
df_capped = df.copy()
for col in numeric_cols:
    Q1  = df[col].quantile(0.25)
    Q3  = df[col].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 0.75 * IQR
    upper = Q3 + 0.75 * IQR

    #Log the station bounds
    logging.info(f"{col:30s}  lower = {lower:.6f}  upper = {upper:.6f}")

    #Clip values outside the [lower, upper] range
    df_capped[col] = df[col].clip(lower=lower, upper=upper)

#Write out the DataFrame and close out the log
df_capped.to_excel(output_path, index=False)
logging.info(f"Capped data written to: {output_path}")
logging.info("Outlier bounds log completed")

print(f"Done!\n"
      f"Capped data → {output_path}\n"
      f"Bounds log  → {log_path}")
