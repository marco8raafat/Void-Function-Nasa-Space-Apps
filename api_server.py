from fastapi import FastAPI
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

# --- Base path ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- CSV path ---
csv_path = os.path.join(BASE_DIR, "data", "weather_cleaned.csv")
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"CSV file not found: {csv_path}")

# --- Load CSV ---
df = pd.read_csv(csv_path)

# --- Target and Features ---
df["RAIN_TODAY"] = (df["PRCP"] > 0).astype(int)

# Season feature
def get_season(month):
    if month in [12, 1, 2]:
        return 0  # Winter
    elif month in [3, 4, 5]:
        return 1  # Spring
    elif month in [6, 7, 8]:
        return 2  # Summer
    else:
        return 3  # Fall

df["SEASON"] = df["MONTH"].apply(get_season)

# Features for API (no temperature)
features = ["SEASON"]
X = df[features]
y = df["RAIN_TODAY"]

# --- Split dataset ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# --- Handle imbalanced data with SMOTE ---
sm = SMOTE(random_state=42)
X_train_res, y_train_res = sm.fit_resample(X_train, y_train)

# --- XGBoost Classifier ---
xgb_model = xgb.XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)
xgb_model.fit(X_train_res, y_train_res)

# --- Predict probabilities ---
xgb_probs = xgb_model.predict_proba(X_test)[:, 1]

# --- Find best threshold to balance Recall & Precision ---
thresholds = np.arange(0.1, 0.9, 0.01)
best_thresh = 0.5
best_score = 0

for t in thresholds:
    preds = (xgb_probs >= t).astype(int)
    rec = recall_score(y_test, preds)
    prec = precision_score(y_test, preds)
    # objective: balance Recall ~0.7 without killing Precision
    score = rec * 0.6 + prec * 0.4  # weighted combination
    if score > best_score and rec <= 0.75:
        best_score = score
        best_thresh = t

# --- Final predictions ---
xgb_preds = (xgb_probs >= best_thresh).astype(int)

# --- Metrics ---
xgb_acc = accuracy_score(y_test, xgb_preds)
xgb_prec = precision_score(y_test, xgb_preds)
xgb_rec = recall_score(y_test, xgb_preds)
xgb_f1 = f1_score(y_test, xgb_preds)

print(f"\n{'='*60}")
print(f"XGBoost Model Training Complete")
print(f"{'='*60}")
print(f"Best Threshold: {best_thresh:.2f}")
print(f"Accuracy:  {xgb_acc:.3f}")
print(f"Precision: {xgb_prec:.3f}")
print(f"Recall:    {xgb_rec:.3f}")
print(f"F1-score:  {xgb_f1:.3f}")
print(f"{'='*60}\n")

# --- Confusion Matrix (save to file) ---
try:
    plt.figure(figsize=(6, 5))
    sns.heatmap(confusion_matrix(y_test, xgb_preds), annot=True, fmt="d", cmap="Greens")
    plt.title("XGBoost Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.savefig(os.path.join(BASE_DIR, 'confusion_matrix.png'))
    plt.close()
    print("✓ Confusion matrix saved to confusion_matrix.png\n")
except Exception as e:
    print(f"⚠ Could not save confusion matrix: {e}\n")

# --- FastAPI ---
app = FastAPI(
    title="NASA Weather Prediction API",
    description="ML-powered weather prediction using XGBoost",
    version="1.0.0"
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
        "model": "XGBoost",
        "version": "1.0.0",
        "metrics": {
            "accuracy": float(xgb_acc),
            "precision": float(xgb_prec),
            "recall": float(xgb_rec),
            "f1_score": float(xgb_f1),
            "threshold": float(best_thresh)
        }
    }

@app.get("/predict")
def predict(lat: float, lon: float, day: int, month: int, year: int):
    """
    Predict rain probability for a given location and date.
    
    Parameters:
    - lat: latitude (-90 to 90)
    - lon: longitude (-180 to 180)
    - day: day of month (1-31)
    - month: month (1-12)
    - year: year
    
    Returns:
    - rain_probability: probability of rain (0-1)
    - rain_predicted: binary prediction (0 or 1)
    - season: season name
    - confidence: model confidence level
    """
    # Calculate season
    season_num = 0 if month in [12, 1, 2] else 1 if month in [3, 4, 5] else 2 if month in [6, 7, 8] else 3
    season_names = {0: "Winter", 1: "Spring", 2: "Summer", 3: "Fall"}
    
    # Create input dataframe
    X_input = pd.DataFrame([{"SEASON": season_num}])
    
    # Get prediction
    prob = xgb_model.predict_proba(X_input)[:, 1][0]
    rain_pred = int(prob >= best_thresh)
    
    # Calculate confidence (distance from threshold)
    confidence = abs(prob - best_thresh) / best_thresh
    confidence = min(confidence, 1.0)  # Cap at 1.0
    
    return {
        "rain_probability": float(prob),
        "rain_predicted": rain_pred,
        "season": season_names[season_num],
        "season_code": season_num,
        "confidence": float(confidence),
        "location": {
            "latitude": lat,
            "longitude": lon
        },
        "date": {
            "day": day,
            "month": month,
            "year": year
        },
        "model_info": {
            "threshold": float(best_thresh),
            "model_accuracy": float(xgb_acc)
        }
    }

@app.get("/model-info")
def model_info():
    """Get detailed model information and performance metrics"""
    return {
        "model_type": "XGBoost Classifier",
        "features": features,
        "training_size": len(X_train_res),
        "test_size": len(X_test),
        "metrics": {
            "accuracy": float(xgb_acc),
            "precision": float(xgb_prec),
            "recall": float(xgb_rec),
            "f1_score": float(xgb_f1)
        },
        "hyperparameters": {
            "n_estimators": 300,
            "learning_rate": 0.05,
            "max_depth": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8
        },
        "threshold": float(best_thresh)
    }

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting NASA Weather Prediction API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("🔄 Interactive API at: http://localhost:8000/redoc\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
