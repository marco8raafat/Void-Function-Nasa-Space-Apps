from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import xarray as xr
import pandas as pd


#Data
files = [
    "data\Air Temperature.nc",
    "data\g4.areaAvgTimeSeries.GLDAS_NOAH10_M_2_1_Rainf_f_tavg.20000101-20250131.180W_60S_180E_90N.nc",
    "data\precipitation.nc",
    "data\seaSurfaceTemp.nc"
]

datasets = [xr.open_dataset(f) for f in files]   

merged = xr.merge(datasets)

print("Variables in merged dataset:")
print(merged.data_vars) 

df = merged.to_dataframe().reset_index()

df.to_csv("weather_25years.csv", index=False)

print(" CSV : weather_25years.csv")

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
