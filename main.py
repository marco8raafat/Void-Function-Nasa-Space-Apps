from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import xarray as xr
import pandas as pd
import os 


#Data
files = [
    "data\Air Temperature.nc",
    "data\g4.areaAvgTimeSeries.GLDAS_NOAH10_M_2_1_Rainf_f_tavg.20000101-20250131.180W_60S_180E_90N.nc",
    "data\precipitation.nc",
    "data\seaSurfaceTemp.nc"
]

# Load datasets
datasets = [xr.open_dataset(f) for f in files]

# datamonth 
cleaned = [ds.drop_vars("datamonth") if "datamonth" in ds.variables else ds for ds in datasets]

# Merge datasets 
merged = xr.merge(cleaned, compat="override")

print(" Variables in merged dataset:")
print(merged.data_vars)

# Convert to DataFrame & Save to CSV
df = merged.to_dataframe().reset_index()
csv_path = "weather_25years.csv"
df.to_csv(csv_path, index=False)

print(f" CSV created: {os.path.abspath(csv_path)}")
#API
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
@app.get("/predict") #endpoint
def predict(lat: float, lon: float):
   
    rain_probability = (float(lat) + float(lon)) % 100 / 100  
    return {"rain_probability": rain_probability}




## Before cleaning 

# Read back the CSV (use csv_path defined above). The default delimiter is ',' so no need
# to pass a delimiter argument.
df = pd.read_csv(csv_path)
print('\n')
print(df.head(50))