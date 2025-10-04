from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import xgboost as xgb
from imblearn.over_sampling import SMOTE
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, Optional
import requests
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from dotenv import load_dotenv
    load_dotenv()
except (ImportError, UnicodeDecodeError) as e:
    # dotenv is optional; proceed if not available or if .env has encoding issues
    if isinstance(e, UnicodeDecodeError):
        print("⚠️ Warning: .env file has encoding issues, skipping dotenv loading")
    pass

# --- Base path ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- CSV path ---
csv_path = os.path.join(BASE_DIR, "data", "weather_cleaned.csv")
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"CSV file not found: {csv_path}")

# --- Load CSV for baseline ---
df_alexandria_base = pd.read_csv(csv_path)

# --- OpenWeatherMap API Configuration ---
POWER_PARAMS = ["T2M_MAX", "T2M_MIN", "T2M", "PRECTOTCORR", "WS2M", "RH2M"]  # temperature, precip, wind speed, humidity
OWM_API_KEY = os.getenv("OPENWEATHER_API_KEY") or os.getenv("OWM_API_KEY")

def _owm_onecall_daily_forecast(lat: float, lon: float) -> pd.DataFrame:
    """Fetch OpenWeatherMap daily forecast data (up to 8 days)"""
    if not OWM_API_KEY:
        raise HTTPException(status_code=500, detail="Missing OPENWEATHER_API_KEY in environment")
    
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "exclude": "minutely,hourly,alerts",
        "units": "metric",
        "appid": OWM_API_KEY,
    }
    
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    
    daily = data.get("daily", [])
    rows = []
    
    for d in daily:
        dt = datetime.utcfromtimestamp(d["dt"]).date()
        temp = d.get("temp", {})
        
        # Handle precipitation (rain + snow in mm)
        rain_mm = d.get("rain", 0.0) or 0.0
        snow_mm = d.get("snow", 0.0) or 0.0
        
        row = {
            "date": pd.to_datetime(dt),
            "T2M_MAX": temp.get("max"),
            "T2M_MIN": temp.get("min"),
            "T2M": np.nanmean([temp.get("min"), temp.get("max")]),
            "PRECTOTCORR": float(rain_mm) + float(snow_mm),  # mm/day
            "WS2M": d.get("wind_speed", np.nan),  # m/s
            "RH2M": d.get("humidity", np.nan),  # %
        }
        rows.append(row)
    
    if not rows:
        return pd.DataFrame(columns=POWER_PARAMS)
    
    df = pd.DataFrame(rows).set_index("date").sort_index()
    return df

def _owm_timemachine_daily(lat: float, lon: float, day: datetime) -> pd.DataFrame:
    """Fetch historical weather data for a single day (up to 5 days back)"""
    if not OWM_API_KEY:
        raise HTTPException(status_code=500, detail="Missing OPENWEATHER_API_KEY in environment")
    
    url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
    dt_unix = int(datetime(day.year, day.month, day.day, 12, 0).timestamp())
    
    params = {
        "lat": lat,
        "lon": lon,
        "dt": dt_unix,
        "units": "metric",
        "appid": OWM_API_KEY,
    }
    
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    
    hourly = data.get("hourly", [])
    if not hourly:
        return pd.DataFrame(columns=POWER_PARAMS, index=[pd.to_datetime(day.date())])
    
    # Aggregate hourly data to daily
    temps = [h.get("temp") for h in hourly if h.get("temp") is not None]
    winds = [h.get("wind_speed") for h in hourly if h.get("wind_speed") is not None]
    hums = [h.get("humidity") for h in hourly if h.get("humidity") is not None]
    
    # Sum precipitation (rain + snow)
    precs = []
    for h in hourly:
        rain = h.get("rain", {})
        snow = h.get("snow", {})
        precs.append((rain.get("1h", 0.0) or 0.0) + (snow.get("1h", 0.0) or 0.0))
    
    row = {
        "T2M_MAX": max(temps) if temps else np.nan,
        "T2M_MIN": min(temps) if temps else np.nan,
        "T2M": float(np.nanmean(temps)) if temps else np.nan,
        "PRECTOTCORR": float(np.nansum(precs)) if precs else 0.0,
        "WS2M": float(np.nanmean(winds)) if winds else np.nan,
        "RH2M": float(np.nanmean(hums)) if hums else np.nan,
    }
    
    df = pd.DataFrame([row], index=[pd.to_datetime(day.date())])
    return df

def fetch_openweather_point(lat: float, lon: float, start_date: datetime, end_date: datetime, params_list: list) -> pd.DataFrame:
    """
    Fetch daily weather data using OpenWeatherMap API.
    Maps to POWER-compatible parameters: T2M_MAX, T2M_MIN, T2M, PRECTOTCORR, WS2M, RH2M
    """
    print(f"🌍 Requesting OpenWeatherMap for ({lat:.2f}, {lon:.2f}) {start_date:%Y-%m-%d} -> {end_date:%Y-%m-%d}")
    
    today = datetime.utcnow().date()
    parts = []
    
    # Historical data (up to 5 days back)
    hist_start = max(start_date.date(), today - timedelta(days=5))
    hist_end = min(end_date.date(), today - timedelta(days=1))
    
    d = hist_start
    while d <= hist_end:
        try:
            parts.append(_owm_timemachine_daily(lat, lon, datetime(d.year, d.month, d.day)))
        except Exception as e:
            print(f"   ⚠️ OWM historical failed for {d}: {e}")
        d += timedelta(days=1)
    
    # Forecast data (today and future)
    if end_date.date() >= today:
        try:
            fdf = _owm_onecall_daily_forecast(lat, lon)
            # Filter to requested date range
            fdf = fdf[(fdf.index.date >= max(start_date.date(), today)) & (fdf.index.date <= end_date.date())]
            if not fdf.empty:
                parts.append(fdf)
        except Exception as e:
            print(f"   ⚠️ OWM forecast failed: {e}")
    
    if not parts:
        raise HTTPException(status_code=500, detail="OpenWeatherMap returned no data for requested range")
    
    df = pd.concat(parts).sort_index()
    
    # Ensure all requested columns exist
    for p in params_list:
        if p not in df.columns:
            df[p] = np.nan
    
    print(f"✅ Successfully fetched {len(df)} days of OpenWeatherMap data")
    return df

# --- Weather Condition Thresholds (Enhanced for Global Use) ---
WEATHER_THRESHOLDS = {
    "very_hot": 95.0,      # T2M_MAX >= 95°F (35°C - globally very hot)
    "very_cold": 32.0,     # T2M_MIN <= 32°F (0°C - freezing point)
    "very_wet": 0.5,       # PRECTOTCORR >= 0.5 inches (heavy rain)
    "very_windy": 25.0,    # WS2M >= 25 mph (strong wind)
    "very_humid": 85.0,    # RH2M >= 85% (very humid)
    "uncomfortable_heat": 104.0,  # T2M_MAX >= 104°F (40°C - extremely hot)
    "uncomfortable_cold": 14.0,   # T2M_MIN <= 14°F (-10°C - extremely cold)
    "high_temp_variation": 36.0,  # T2M_MAX - T2M_MIN >= 36°F (20°C - high variation)
    "heat_index_dangerous": 105.0  # Calculated heat index threshold
}

def calculate_heat_index(temp_f: float, humidity: float) -> float:
    """Calculate heat index (feels like temperature) using temperature in Fahrenheit and relative humidity."""
    if temp_f < 80:
        return temp_f
    
    # Rothfusz regression coefficients for heat index calculation
    c1 = -42.379
    c2 = 2.04901523
    c3 = 10.14333127
    c4 = -0.22475541
    c5 = -6.83783e-3
    c6 = -5.481717e-2
    c7 = 1.22874e-3
    c8 = 8.5282e-4
    c9 = -1.99e-6
    
    hi = (c1 + (c2 * temp_f) + (c3 * humidity) + (c4 * temp_f * humidity) +
          (c5 * temp_f * temp_f) + (c6 * humidity * humidity) +
          (c7 * temp_f * temp_f * humidity) + (c8 * temp_f * humidity * humidity) +
          (c9 * temp_f * temp_f * humidity * humidity))
    
    return hi

def process_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process weather data (POWER-like columns from OpenWeatherMap) to match our model format and add derived features."""
    processed_df = df.copy()
    
    # Convert temperature from Celsius to Fahrenheit
    processed_df['TMAX'] = (processed_df['T2M_MAX'] * 9/5) + 32
    processed_df['TMIN'] = (processed_df['T2M_MIN'] * 9/5) + 32
    processed_df['TAVG'] = (processed_df['T2M'] * 9/5) + 32
    
    # Convert precipitation from mm to inches
    processed_df['PRCP'] = processed_df['PRECTOTCORR'] / 25.4
    
    # Add wind speed (already in m/s, convert to mph for consistency)
    processed_df['WIND_SPEED'] = processed_df['WS2M'] * 2.237  # m/s to mph
    
    # Add humidity (already in percentage)
    processed_df['HUMIDITY'] = processed_df['RH2M']
    
    # Calculate heat index
    processed_df['HEAT_INDEX'] = processed_df.apply(
        lambda row: calculate_heat_index(row['TMAX'], row['HUMIDITY']), axis=1
    )
    
    # Add date components
    processed_df['YEAR'] = processed_df.index.year
    processed_df['MONTH'] = processed_df.index.month
    processed_df['DAY'] = processed_df.index.day
    
    # Add season
    processed_df['SEASON'] = processed_df['MONTH'].apply(get_season)
    
    return processed_df

def create_enhanced_weather_targets(df: pd.DataFrame) -> Dict:
    """Create target variables for enhanced weather conditions using NASA POWER data."""
    targets = {
        "rain": (df["PRCP"] > 0).astype(int),
        "very_hot": (df["TMAX"] >= WEATHER_THRESHOLDS["very_hot"]).astype(int),
        "very_cold": (df["TMIN"] <= WEATHER_THRESHOLDS["very_cold"]).astype(int),
        "very_wet": (df["PRCP"] >= WEATHER_THRESHOLDS["very_wet"]).astype(int),
        "very_windy": (df["WIND_SPEED"] >= WEATHER_THRESHOLDS["very_windy"]).astype(int),
        "very_humid": (df["HUMIDITY"] >= WEATHER_THRESHOLDS["very_humid"]).astype(int),
        "uncomfortable": (
            (df["TMAX"] >= WEATHER_THRESHOLDS["uncomfortable_heat"]) |
            (df["TMIN"] <= WEATHER_THRESHOLDS["uncomfortable_cold"]) |
            ((df["TMAX"] - df["TMIN"]) >= WEATHER_THRESHOLDS["high_temp_variation"]) |
            (df["HEAT_INDEX"] >= WEATHER_THRESHOLDS["heat_index_dangerous"])
        ).astype(int)
    }
    return targets

# Season feature function
def get_season(month):
    if month in [12, 1, 2]:
        return 0  # Winter
    elif month in [3, 4, 5]:
        return 1  # Spring
    elif month in [6, 7, 8]:
        return 2  # Summer
    else:
        return 3  # Fall

# --- Enhanced Data Loading and Processing ---
print("🔄 Loading and processing training data for multi-location weather prediction...")

# Process Alexandria baseline data
df_alexandria_base["SEASON"] = df_alexandria_base["MONTH"].apply(get_season)
df_alexandria_base["WIND_SPEED"] = 10.0  # Estimated average wind speed
df_alexandria_base["HUMIDITY"] = 65.0    # Estimated average humidity  
df_alexandria_base["HEAT_INDEX"] = df_alexandria_base.apply(
    lambda row: calculate_heat_index(row['TMAX'], 65.0), axis=1
)

# Collect training data (baseline CSV only to avoid API limits during startup)
all_training_data = [df_alexandria_base]

# Skip external training data to avoid OpenWeatherMap API limits during startup
# Enable only if you have unlimited API calls and want global training data
print("🌍 Using baseline training data only (avoiding external API calls during startup)")

# Combine all training data
print("🔗 Combining training data from all sources...")
df = pd.concat(all_training_data, ignore_index=True, sort=False)
print(f"📊 Total training samples: {len(df)}")

# Enhanced features including all available parameters
features = ["SEASON", "TAVG", "TMAX", "TMIN", "MONTH", "DAY", "WIND_SPEED", "HUMIDITY", "HEAT_INDEX"]

# Ensure all required columns exist and handle missing values
for feature in features:
    if feature not in df.columns:
        if feature == "WIND_SPEED":
            df[feature] = 10.0  # Default wind speed
        elif feature == "HUMIDITY":
            df[feature] = 65.0  # Default humidity
        elif feature == "HEAT_INDEX":
            df[feature] = df["TMAX"]  # Fallback to max temp

X = df[features].fillna(df[features].mean())

# Create enhanced target variables
targets = create_enhanced_weather_targets(df)

print("📋 Weather conditions in training data:")
for condition, target in targets.items():
    pos_samples = target.sum()
    total_samples = len(target)
    percentage = (pos_samples / total_samples * 100) if total_samples > 0 else 0
    print(f"  - {condition}: {pos_samples}/{total_samples} ({percentage:.1f}%)")

# --- Train Multiple Models ---
models = {}
thresholds = {}
metrics = {}

print(f"\n{'='*60}")
print(f"Training Multiple Weather Condition Models")
print(f"{'='*60}")

for condition_name, y in targets.items():
    print(f"\n🔄 Training model for: {condition_name.upper()}")
    
    # Skip if no positive samples or only one class
    if y.sum() == 0 or y.sum() == len(y):
        print(f"⚠ Skipping {condition_name} - insufficient class diversity")
        continue
    
    # Split dataset with stratification fallback
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    except ValueError as e:
        print(f"   ⚠️ Stratified split failed for {condition_name}: {e}")
        print(f"   Using non-stratified split instead")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
    
    # Handle imbalanced data with SMOTE (if needed)
    if y_train.sum() > 1 and len(y_train) - y_train.sum() > 1:  # Need at least 2 samples of each class
        sm = SMOTE(random_state=42)
        X_train_res, y_train_res = sm.fit_resample(X_train, y_train)
    else:
        X_train_res, y_train_res = X_train, y_train
    
    # XGBoost Classifier
    model = xgb.XGBClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    model.fit(X_train_res, y_train_res)
    
    # Predict probabilities
    probs = model.predict_proba(X_test)[:, 1]
    
    # Find best threshold
    thresh_range = np.arange(0.1, 0.9, 0.01)
    best_thresh = 0.5
    best_score = 0
    
    for t in thresh_range:
        preds = (probs >= t).astype(int)
        if len(np.unique(preds)) > 1:  # Ensure we have both classes
            rec = recall_score(y_test, preds, zero_division=0)
            prec = precision_score(y_test, preds, zero_division=0)
            score = rec * 0.6 + prec * 0.4  # weighted combination
            if score > best_score:
                best_score = score
                best_thresh = t
    
    # Final predictions with best threshold
    final_preds = (probs >= best_thresh).astype(int)
    
    # Calculate metrics
    acc = accuracy_score(y_test, final_preds)
    prec = precision_score(y_test, final_preds, zero_division=0)
    rec = recall_score(y_test, final_preds, zero_division=0)
    f1 = f1_score(y_test, final_preds, zero_division=0)
    
    # Store results
    models[condition_name] = model
    thresholds[condition_name] = best_thresh
    metrics[condition_name] = {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1
    }
    
    print(f"  ✓ Accuracy: {acc:.3f}, Precision: {prec:.3f}, Recall: {rec:.3f}, F1: {f1:.3f}")
    print(f"  ✓ Best threshold: {best_thresh:.3f}")

# For backward compatibility, use rain model as main model
xgb_model = models.get("rain")
best_thresh = thresholds.get("rain", 0.5)
if "rain" in metrics:
    xgb_acc = metrics["rain"]["accuracy"]
    xgb_prec = metrics["rain"]["precision"] 
    xgb_rec = metrics["rain"]["recall"]
    xgb_f1 = metrics["rain"]["f1_score"]
else:
    xgb_acc = xgb_prec = xgb_rec = xgb_f1 = 0.0

print(f"\n{'='*60}")
print(f"Multi-Condition Weather Models Training Complete")
print(f"{'='*60}")

# Print summary of all models
for condition, model_metrics in metrics.items():
    print(f"{condition.upper()}: Acc={model_metrics['accuracy']:.3f}, "
          f"Prec={model_metrics['precision']:.3f}, "
          f"Rec={model_metrics['recall']:.3f}, "
          f"F1={model_metrics['f1_score']:.3f}")

print(f"{'='*60}\n")

# --- Create visualization of condition distributions ---
try:
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, (condition_name, y) in enumerate(targets.items()):
        if i < len(axes):
            condition_counts = y.value_counts()
            axes[i].bar(["Normal", "Condition Present"], condition_counts.values)
            axes[i].set_title(f"{condition_name.replace('_', ' ').title()}")
            axes[i].set_ylabel("Count")
    
    # Hide extra subplot
    if len(targets) < len(axes):
        axes[-1].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, 'weather_conditions_distribution.png'))
    plt.close()
    print("✓ Weather conditions distribution saved to weather_conditions_distribution.png\n")
except Exception as e:
    print(f"⚠ Could not save weather conditions visualization: {e}\n")

# --- FastAPI ---
app = FastAPI(
    title="OpenWeatherMap Weather Prediction API",
    description="ML-powered weather prediction using XGBoost with OpenWeatherMap data",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "online",
        "model": "Multi-Condition Weather Prediction (XGBoost ensemble)",
        "version": "2.0.0",
        "available_predictions": [
            f"very_hot (≥{WEATHER_THRESHOLDS['very_hot']}°F max temperature)",
            f"very_cold (≤{WEATHER_THRESHOLDS['very_cold']}°F min temperature)", 
            f"very_wet (≥{WEATHER_THRESHOLDS['very_wet']} inches precipitation)",
            f"very_windy (≥{WEATHER_THRESHOLDS['very_windy']} mph wind speed)",
            f"very_humid (≥{WEATHER_THRESHOLDS['very_humid']}% relative humidity)",
            "uncomfortable (extreme/dangerous conditions)",
            "rain (any measurable precipitation)"
        ],
        "models_trained": len(models),
        "weather_thresholds": WEATHER_THRESHOLDS,
        "model_metrics": {name: metrics[name] for name in metrics.keys()}
    }

@app.get("/predict")
def predict(lat: float, lon: float, day: int, month: int, year: int, use_real_data: bool = True):
    """
    Predict comprehensive weather conditions for a given location and date using OpenWeatherMap data.
    
    Parameters:
    - lat: latitude (-90 to 90)
    - lon: longitude (-180 to 180)  
    - day: day of month (1-31)
    - month: month (1-12)
    - year: year
    - use_real_data: if True, fetch real OpenWeatherMap data; if False, use estimates
    
    Returns comprehensive weather condition predictions including:
    - Likelihood of very hot conditions (≥95°F max temp)
    - Likelihood of very cold conditions (≤32°F min temp)
    - Likelihood of very wet conditions (≥0.5 inches precipitation)
    - Likelihood of very windy conditions (≥25 mph wind speed)
    - Likelihood of very humid conditions (≥85% humidity)
    - Likelihood of uncomfortable conditions (extreme conditions)
    """
    season_num = get_season(month)
    season_names = {0: "Winter", 1: "Spring", 2: "Summer", 3: "Fall"}
    
    # Try to fetch real OpenWeatherMap data for the location
    if use_real_data:
        try:
            target_date = datetime(year, month, day)
            # Fetch data around the target date (limited by OWM: 5 days history + 8 days forecast)
            start_date = target_date - timedelta(days=5)
            end_date = target_date + timedelta(days=8)
            
            print(f"🌍 Fetching OpenWeatherMap data for ({lat:.2f}, {lon:.2f}) around {target_date.date()}")
            owm_df = fetch_openweather_point(lat, lon, start_date, end_date, POWER_PARAMS)
            processed_df = process_weather_data(owm_df)
            
            # Use the closest available date or average if target date not available
            if len(processed_df) > 0:
                target_date_str = target_date.strftime("%Y-%m-%d")
                
                if target_date_str in processed_df.index.strftime("%Y-%m-%d"):
                    # Exact date available
                    actual_data = processed_df[processed_df.index.strftime("%Y-%m-%d") == target_date_str].iloc[0]
                    estimated_tavg = actual_data['TAVG']
                    estimated_tmax = actual_data['TMAX'] 
                    estimated_tmin = actual_data['TMIN']
                    estimated_wind = actual_data['WIND_SPEED']
                    estimated_humidity = actual_data['HUMIDITY']
                    estimated_heat_index = actual_data['HEAT_INDEX']
                    data_source = "openweathermap_exact"
                else:
                    # Use recent average (seasonal behavior)
                    same_season = processed_df[processed_df['SEASON'] == season_num]
                    if len(same_season) > 0:
                        estimated_tavg = same_season['TAVG'].mean()
                        estimated_tmax = same_season['TMAX'].mean()
                        estimated_tmin = same_season['TMIN'].mean()
                        estimated_wind = same_season['WIND_SPEED'].mean()
                        estimated_humidity = same_season['HUMIDITY'].mean()
                        estimated_heat_index = same_season['HEAT_INDEX'].mean()
                        data_source = "openweathermap_seasonal"
                    else:
                        # Fallback to overall average
                        estimated_tavg = processed_df['TAVG'].mean()
                        estimated_tmax = processed_df['TMAX'].mean()
                        estimated_tmin = processed_df['TMIN'].mean()
                        estimated_wind = processed_df['WIND_SPEED'].mean()
                        estimated_humidity = processed_df['HUMIDITY'].mean()
                        estimated_heat_index = processed_df['HEAT_INDEX'].mean()
                        data_source = "openweathermap_average"
                        
                print(f"✅ Using OpenWeatherMap data source: {data_source}")
                
            else:
                raise ValueError("No OpenWeatherMap data available")
                
        except Exception as e:
            print(f"⚠️ OpenWeatherMap data unavailable ({e}), falling back to climate estimates")
            use_real_data = False
    
    # Fallback to climate-based estimates if NASA POWER data is unavailable
    if not use_real_data:
        # Enhanced climate estimates based on latitude and season
        seasonal_base = {
            0: {"tavg": 45, "tmax": 55, "tmin": 35},  # Winter
            1: {"tavg": 65, "tmax": 75, "tmin": 55},  # Spring  
            2: {"tavg": 80, "tmax": 90, "tmin": 70},  # Summer
            3: {"tavg": 60, "tmax": 70, "tmin": 50}   # Fall
        }
        
        # Adjust for latitude (more sophisticated than before)
        lat_factor = np.cos(np.radians(lat)) * 0.8  # Latitudinal temperature variation
        seasonal_factor = 1.0 + (abs(lat) / 90.0) * 0.3  # Seasonal variation increases with latitude
        
        base = seasonal_base[season_num]
        estimated_tavg = base["tavg"] + (lat_factor * 10) * (1 if lat > 0 else -1)
        estimated_tmax = base["tmax"] + (lat_factor * 12) * (1 if lat > 0 else -1)
        estimated_tmin = base["tmin"] + (lat_factor * 8) * (1 if lat > 0 else -1)
        
        # Estimate other parameters based on location and season
        estimated_wind = 12.0 + np.random.normal(0, 3)  # Base wind with variation
        estimated_humidity = 60.0 + (20 * np.cos(np.radians(lat * 2)))  # Humidity pattern
        estimated_heat_index = calculate_heat_index(estimated_tmax, estimated_humidity)
        data_source = "climate_estimate"
        
        print(f"📊 Using climate-based estimates for ({lat:.2f}, {lon:.2f})")
    
    # Create input dataframe with all enhanced features
    X_input = pd.DataFrame([{
        "SEASON": season_num,
        "TAVG": estimated_tavg,
        "TMAX": estimated_tmax, 
        "TMIN": estimated_tmin,
        "MONTH": month,
        "DAY": day,
        "WIND_SPEED": estimated_wind,
        "HUMIDITY": estimated_humidity,
        "HEAT_INDEX": estimated_heat_index
    }])
    
    # Get predictions for all weather conditions
    weather_predictions = {}
    condition_details = {}
    
    for condition_name, model in models.items():
        if model is not None:
            try:
                prob = model.predict_proba(X_input)[:, 1][0]
                thresh = thresholds[condition_name]
                prediction = int(prob >= thresh)
                
                # Calculate confidence 
                confidence = abs(prob - thresh) / max(thresh, 0.1)
                confidence = min(confidence, 1.0)
                
                weather_predictions[condition_name] = {
                    "probability": float(prob),
                    "predicted": prediction,
                    "confidence": float(confidence),
                    "threshold": float(thresh)
                }
                
                # Add human-readable descriptions with enhanced conditions
                condition_details[condition_name] = {
                    "very_hot": {
                        "description": f"Very hot conditions (≥{WEATHER_THRESHOLDS['very_hot']}°F max temperature)",
                        "impact": "Extreme heat stress, stay hydrated, seek air conditioning, avoid outdoor activities"
                    },
                    "very_cold": {
                        "description": f"Very cold conditions (≤{WEATHER_THRESHOLDS['very_cold']}°F min temperature)",
                        "impact": "Risk of hypothermia, dress in layers, protect extremities, limit exposure"
                    },
                    "very_wet": {
                        "description": f"Heavy precipitation (≥{WEATHER_THRESHOLDS['very_wet']} inches expected)",
                        "impact": "Flash flooding possible, avoid low-lying areas, postpone travel"
                    },
                    "very_windy": {
                        "description": f"Very windy conditions (≥{WEATHER_THRESHOLDS['very_windy']} mph wind speed)",
                        "impact": "Strong winds may damage property, avoid outdoor activities, secure loose objects"
                    },
                    "very_humid": {
                        "description": f"Very humid conditions (≥{WEATHER_THRESHOLDS['very_humid']}% relative humidity)",
                        "impact": "Heat index elevated, increased discomfort, stay hydrated, seek air conditioning"
                    },
                    "uncomfortable": {
                        "description": "Uncomfortable conditions (extreme temperatures, high variation, or dangerous heat index)",
                        "impact": "Weather may feel very unpleasant, plan indoor activities, monitor health"
                    },
                    "rain": {
                        "description": "General rain conditions (any measurable precipitation)",
                        "impact": "Bring umbrella, roads may be slippery, allow extra travel time"
                    }
                }.get(condition_name, {
                    "description": f"Weather condition: {condition_name}",
                    "impact": "Monitor weather conditions and plan accordingly"
                })
                    
            except Exception as e:
                print(f"Error predicting {condition_name}: {e}")
                weather_predictions[condition_name] = {
                    "probability": 0.0,
                    "predicted": 0,
                    "confidence": 0.0,
                    "threshold": 0.5
                }
    
    # Create comprehensive summary assessment
    high_risk_conditions = [name for name, pred in weather_predictions.items() 
                          if pred["predicted"] == 1]
    
    # Determine overall comfort level based on predicted conditions
    comfort_score = 100
    comfort_factors = []
    
    if "uncomfortable" in high_risk_conditions:
        comfort_score -= 40
        comfort_factors.append("extreme weather conditions")
    if "very_hot" in high_risk_conditions:
        comfort_score -= 30
        comfort_factors.append("dangerous heat")
    if "very_cold" in high_risk_conditions:
        comfort_score -= 30
        comfort_factors.append("extreme cold")
    if "very_wet" in high_risk_conditions:
        comfort_score -= 20
        comfort_factors.append("heavy precipitation")
    if "very_windy" in high_risk_conditions:
        comfort_score -= 15
        comfort_factors.append("strong winds")
    if "very_humid" in high_risk_conditions:
        comfort_score -= 15
        comfort_factors.append("high humidity")
    if "rain" in high_risk_conditions:
        comfort_score -= 10
        comfort_factors.append("precipitation")
    
    # Determine comfort level
    if comfort_score >= 80:
        overall_comfort = "very comfortable"
    elif comfort_score >= 60:
        overall_comfort = "comfortable"
    elif comfort_score >= 40:
        overall_comfort = "somewhat uncomfortable"
    elif comfort_score >= 20:
        overall_comfort = "uncomfortable"
    else:
        overall_comfort = "very uncomfortable"
        
    return {
        "weather_conditions": weather_predictions,
        "condition_details": condition_details,
        "summary": {
            "overall_comfort": overall_comfort,
            "comfort_score": comfort_score,
            "comfort_factors": comfort_factors,
            "high_risk_conditions": high_risk_conditions,
            "season": season_names[season_num],
            "data_source": data_source,
            "weather_parameters": {
                "temperature": {
                    "average": round(estimated_tavg, 1),
                    "maximum": round(estimated_tmax, 1),
                    "minimum": round(estimated_tmin, 1),
                    "heat_index": round(estimated_heat_index, 1)
                },
                "wind_speed_mph": round(estimated_wind, 1),
                "humidity_percent": round(estimated_humidity, 1)
            }
        },
        "location": {
            "latitude": lat,
            "longitude": lon
        },
        "date": {
            "day": day,
            "month": month,
            "year": year
        },
        "thresholds": WEATHER_THRESHOLDS,
        "model_performance": {name: metrics[name] for name in metrics.keys() if name in metrics}
    }

@app.get("/model-info")
def model_info():
    """Get detailed model information and performance metrics for all weather conditions"""
    return {
        "model_type": "Multi-Condition XGBoost Classifier Ensemble",
        "version": "2.0.0",
        "features": features,
        "weather_conditions": list(models.keys()),
        "weather_thresholds": WEATHER_THRESHOLDS,
        "models": {
            condition: {
                "metrics": metrics[condition],
                "threshold": thresholds[condition],
                "trained": condition in models and models[condition] is not None
            } for condition in models.keys()
        },
        "hyperparameters": {
            "n_estimators": 200,
            "learning_rate": 0.1,
            "max_depth": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8
        },
        "data_info": {
            "total_samples": len(df),
            "location": "Alexandria, Egypt (Mediterranean climate)",
            "date_range": f"{df['YEAR'].min()}-{df['YEAR'].max()}",
            "features_used": features
        }
    }

@app.get("/conditions")
def get_conditions():
    """Get information about all weather conditions that can be predicted"""
    return {
        "conditions": {
            "very_hot": {
                "threshold": f"≥{WEATHER_THRESHOLDS['very_hot']}°F maximum temperature",
                "description": "Extremely hot conditions that pose serious health risks",
                "recommendations": ["Stay indoors with AC", "Drink water frequently", "Avoid strenuous outdoor activities", "Check on elderly/vulnerable people"]
            },
            "very_cold": {
                "threshold": f"≤{WEATHER_THRESHOLDS['very_cold']}°F minimum temperature", 
                "description": "Freezing conditions that may cause hypothermia or frostbite",
                "recommendations": ["Dress in layers", "Cover exposed skin", "Stay dry", "Limit time outdoors", "Check heating systems"]
            },
            "very_wet": {
                "threshold": f"≥{WEATHER_THRESHOLDS['very_wet']} inches precipitation",
                "description": "Heavy precipitation that may cause flooding and travel hazards",
                "recommendations": ["Avoid flood-prone areas", "Don't drive through standing water", "Monitor weather alerts", "Secure outdoor items"]
            },
            "very_windy": {
                "threshold": f"≥{WEATHER_THRESHOLDS['very_windy']} mph wind speed",
                "description": "Strong winds that may damage property and pose safety risks",
                "recommendations": ["Secure loose objects", "Avoid tall trees and structures", "Drive carefully", "Postpone outdoor activities"]
            },
            "very_humid": {
                "threshold": f"≥{WEATHER_THRESHOLDS['very_humid']}% relative humidity",
                "description": "Very high humidity that increases heat index and discomfort",
                "recommendations": ["Stay in air conditioning", "Drink extra fluids", "Take frequent breaks", "Wear lightweight clothing"]
            },
            "uncomfortable": {
                "threshold": f"Multiple factors: ≥{WEATHER_THRESHOLDS['uncomfortable_heat']}°F max, ≤{WEATHER_THRESHOLDS['uncomfortable_cold']}°F min, ≥{WEATHER_THRESHOLDS['high_temp_variation']}°F variation, or ≥{WEATHER_THRESHOLDS['heat_index_dangerous']}°F heat index",
                "description": "Combination of extreme weather conditions creating dangerous or very unpleasant conditions",
                "recommendations": ["Stay indoors when possible", "Monitor health symptoms", "Follow all relevant weather warnings", "Have emergency supplies ready"]
            },
            "rain": {
                "threshold": "Any measurable precipitation > 0 inches",
                "description": "General precipitation conditions",
                "recommendations": ["Carry umbrella", "Allow extra travel time", "Drive with caution", "Wear appropriate footwear"]
            }
        },
        "model_performance": {name: metrics[name] for name in metrics.keys()}
    }

@app.get("/fetch-openweather-data")
def fetch_openweather_data(lat: float, lon: float, days: int = 7):
    """
    Test endpoint to fetch raw OpenWeatherMap data for a location.
    
    Parameters:
    - lat: latitude (-90 to 90)
    - lon: longitude (-180 to 180)
    - days: number of days to fetch (max: 5 history + 8 forecast)
    
    Returns raw and processed OpenWeatherMap data for testing/verification.
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        print(f"🌍 Test fetch: OpenWeatherMap data for ({lat:.2f}, {lon:.2f})")
        raw_df = fetch_openweather_point(lat, lon, start_date, end_date, POWER_PARAMS)
        processed_df = process_weather_data(raw_df)
        
        # Calculate some basic statistics
        stats = {}
        for col in ['TMAX', 'TMIN', 'TAVG', 'PRCP', 'WIND_SPEED', 'HUMIDITY']:
            if col in processed_df.columns:
                stats[col] = {
                    "mean": float(processed_df[col].mean()),
                    "min": float(processed_df[col].min()),
                    "max": float(processed_df[col].max()),
                    "std": float(processed_df[col].std())
                }
        
        return {
            "status": "success",
            "location": {"latitude": lat, "longitude": lon},
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "days_requested": days,
                "days_received": len(processed_df)
            },
            "statistics": stats,
            "sample_data": processed_df.head(5).to_dict('records') if len(processed_df) > 0 else [],
            "data_quality": {
                "completeness": f"{(processed_df.notna().sum().sum() / processed_df.size * 100):.1f}%",
                "missing_values": processed_df.isna().sum().to_dict()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch OpenWeatherMap data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting OpenWeatherMap Weather Prediction API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("🔄 Interactive API at: http://localhost:8000/redoc")
    print("\n🌍 Features:")
    print("   - Real-time OpenWeatherMap data integration (5 days history + 8 days forecast)")
    print("   - Enhanced weather conditions: hot, cold, wet, windy, humid, uncomfortable")
    print("   - Global climate modeling with location-specific adjustments")
    print("   - Comprehensive comfort scoring and risk assessment")
    print(f"   - {len(models)} trained models for different weather conditions")
    print(f"   - Enhanced thresholds: {len(WEATHER_THRESHOLDS)} weather parameters")
    print("\n📊 API Endpoints:")
    print("   - GET /predict - Comprehensive weather prediction with OpenWeatherMap data")
    print("   - GET /fetch-openweather-data - Test OpenWeatherMap data retrieval")
    print("   - GET /conditions - Detailed condition information and recommendations")
    print("   - GET /model-info - Enhanced model performance and training data info")
    print("\n✨ To test the enhanced API, run: python test_enhanced_api.py")
    print("=" * 80)
    uvicorn.run(app, host="0.0.0.0", port=8000)
