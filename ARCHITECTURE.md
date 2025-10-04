# 🏗️ Architecture & Data Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
│                    http://localhost:5000                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Requests
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Pages:                                                  │   │
│  │  • weather.tsx - Main prediction interface              │   │
│  │  • home.tsx - Landing page                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Components:                                             │   │
│  │  • WeatherMap - Interactive location selector           │   │
│  │  • Forms - Input validation with React Hook Form        │   │
│  │  • UI Components - Shadcn/ui library                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ /api/predict
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Express.js Backend (Port 5000)                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Routes (server/routes.ts):                             │   │
│  │  • GET /api/predict - Proxy to ML backend               │   │
│  │  • GET /api/ml-status - Health check                    │   │
│  │  • GET /api/model-info - Model metadata                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Proxy
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI ML Backend (Port 8000)                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Endpoints (api_server.py):                             │   │
│  │  • GET / - Health & metrics                             │   │
│  │  • GET /predict - Rain prediction                       │   │
│  │  • GET /model-info - Detailed model info                │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ML Model:                                               │   │
│  │  • Algorithm: XGBoost Classifier                        │   │
│  │  • Feature: Season (derived from month)                 │   │
│  │  • Training: SMOTE oversampling                         │   │
│  │  • Output: Probability + Binary prediction              │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Data:                                                   │   │
│  │  • Source: data/weather_cleaned.csv                     │   │
│  │  • 25 years of weather data                             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow

### Prediction Request Flow

```
1. User Action
   ↓
   User clicks map or enters coordinates
   ↓
   Form submission with: {lat, lon, date}

2. Frontend Processing
   ↓
   weather.tsx validates input
   ↓
   Parses date into day/month/year
   ↓
   Calls: fetch('/api/predict?lat=X&lon=Y&day=D&month=M&year=Y')

3. Express Backend
   ↓
   routes.ts receives request
   ↓
   Proxies to: http://localhost:8000/predict
   ↓
   Returns response to frontend

4. FastAPI Backend
   ↓
   api_server.py processes request
   ↓
   Calculates season from month
   ↓
   Creates feature vector: {SEASON: season_code}
   ↓
   XGBoost model predicts rain probability
   ↓
   Applies threshold to get binary prediction
   ↓
   Returns JSON response

5. Frontend Display
   ↓
   weather.tsx receives prediction
   ↓
   Updates UI with:
   • Rain probability percentage
   • Binary prediction (Rain/No Rain)
   • Season information
   • Confidence score
   ↓
   Shows toast notification
```

## Data Flow Diagram

```
┌─────────────┐
│   User      │
│  Browser    │
└──────┬──────┘
       │
       │ 1. Click map (lat: 30.04, lon: 31.23)
       │ 2. Select date (2024-06-15)
       │ 3. Submit form
       ▼
┌──────────────────┐
│  weather.tsx     │
│  Form Handler    │
└──────┬───────────┘
       │
       │ GET /api/predict?lat=30.04&lon=31.23
       │                   &day=15&month=6&year=2024
       ▼
┌──────────────────┐
│  Express Proxy   │
│  routes.ts       │
└──────┬───────────┘
       │
       │ Forward request to ML backend
       ▼
┌──────────────────┐
│   FastAPI        │
│  /predict        │
└──────┬───────────┘
       │
       │ 1. month=6 → season=2 (Summer)
       │ 2. Create DataFrame: {SEASON: 2}
       │ 3. model.predict_proba()
       │ 4. Apply threshold
       ▼
┌──────────────────┐
│  XGBoost Model   │
│  Prediction      │
└──────┬───────────┘
       │
       │ Return: {
       │   rain_probability: 0.65,
       │   rain_predicted: 1,
       │   season: "Summer",
       │   confidence: 0.30,
       │   ...
       │ }
       ▼
┌──────────────────┐
│  Frontend UI     │
│  Results Card    │
└──────────────────┘
```

## Technology Stack

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **Routing:** Wouter
- **State:** React Hook Form
- **Validation:** Zod
- **UI Library:** Shadcn/ui (Radix UI + Tailwind CSS)
- **HTTP Client:** Fetch API
- **Maps:** Leaflet

### Backend - Express
- **Runtime:** Node.js
- **Framework:** Express.js
- **Language:** TypeScript
- **Purpose:** Serve frontend + API proxy

### Backend - FastAPI
- **Language:** Python 3.8+
- **Framework:** FastAPI
- **Server:** Uvicorn
- **ML Library:** XGBoost
- **Data Processing:** Pandas, NumPy
- **Data Balancing:** imbalanced-learn (SMOTE)
- **Visualization:** Matplotlib, Seaborn

## Model Architecture

```
Input: Month (1-12)
  ↓
Season Calculation:
  • Winter (12, 1, 2) → 0
  • Spring (3, 4, 5) → 1
  • Summer (6, 7, 8) → 2
  • Fall (9, 10, 11) → 3
  ↓
Feature Vector: [SEASON]
  ↓
XGBoost Classifier:
  • n_estimators: 300
  • learning_rate: 0.05
  • max_depth: 6
  • subsample: 0.8
  • colsample_bytree: 0.8
  ↓
Probability Output: 0.0 - 1.0
  ↓
Threshold Application: >= best_thresh
  ↓
Binary Prediction: 0 (No Rain) or 1 (Rain)
```

## File Structure

```
.
├── api_server.py              # FastAPI ML backend
├── requirements.txt           # Python dependencies
├── start.ps1                  # Windows PowerShell startup script
├── start.bat                  # Windows batch startup script
├── health-check.ps1           # System health check utility
├── QUICKSTART.md              # Quick start guide
├── README_INTEGRATION.md      # Detailed integration docs
├── ARCHITECTURE.md            # This file
│
├── data/
│   └── weather_cleaned.csv    # 25 years of weather data
│
└── Frontend/
    ├── package.json           # Node.js dependencies
    ├── vite.config.ts         # Vite configuration
    ├── tsconfig.json          # TypeScript configuration
    │
    ├── client/                # React frontend
    │   ├── src/
    │   │   ├── App.tsx        # Main app component
    │   │   ├── pages/
    │   │   │   ├── home.tsx   # Landing page
    │   │   │   └── weather.tsx # Prediction page
    │   │   ├── components/
    │   │   │   ├── weather-map.tsx
    │   │   │   └── ui/        # Shadcn components
    │   │   └── lib/
    │   │       └── utils.ts   # Utilities
    │
    ├── server/                # Express backend
    │   ├── index.ts           # Server entry point
    │   ├── routes.ts          # API routes (proxy)
    │   └── vite.ts            # Vite dev server
    │
    └── shared/
        └── schema.ts          # Shared TypeScript types
```

## Security Considerations

- **CORS:** Currently set to allow all origins (`*`) - should be restricted in production
- **Input Validation:** Zod schema validation on frontend + FastAPI parameter validation
- **Error Handling:** Comprehensive error handling with user-friendly messages
- **API Keys:** None required (local ML model)

## Performance Considerations

- **Model Loading:** XGBoost model loaded once at startup
- **Prediction Speed:** < 100ms per prediction
- **Caching:** None implemented (predictions are deterministic by season)
- **Concurrent Requests:** FastAPI handles async requests efficiently

## Future Enhancements

1. **Location-Based Features:**
   - Use lat/lon for location-specific predictions
   - Add elevation data
   - Include climate zone classification

2. **Additional Features:**
   - Historical weather patterns
   - Atmospheric pressure
   - Humidity levels
   - Wind speed/direction

3. **Model Improvements:**
   - Ensemble methods
   - Time series forecasting
   - Multi-day predictions

4. **UI Enhancements:**
   - Multi-day forecast view
   - Historical prediction accuracy
   - Weather radar overlay
   - Mobile app version

5. **Production Ready:**
   - Docker containerization
   - Kubernetes deployment
   - Redis caching
   - Database for prediction logs
   - User authentication
