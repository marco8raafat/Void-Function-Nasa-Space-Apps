# NASA Weather Prediction App - Integration Guide

This project integrates a FastAPI ML backend with a React/TypeScript frontend for weather prediction.

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   React Frontend│─────▶│  Express Server  │─────▶│ FastAPI ML API  │
│   (Port 5000)   │      │  (Port 5000)     │      │  (Port 8000)    │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                  │
                                  │ Proxy
                                  ▼
                         /api/predict endpoint
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn**

### 1. Install Python Dependencies

```powershell
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Node.js Dependencies

```powershell
cd Frontend
npm install
```

### 3. Start the ML Backend (FastAPI)

In **Terminal 1** (from project root):

```powershell
# Activate virtual environment if not already active
.\venv\Scripts\Activate.ps1

# Start FastAPI server
python api_server.py
```

The API will be available at:
- 🌐 API: http://localhost:8000
- 📖 Swagger Docs: http://localhost:8000/docs
- 📘 ReDoc: http://localhost:8000/redoc

### 4. Start the Frontend

In **Terminal 2**:

```powershell
cd Frontend
npm run dev
```

The frontend will be available at:
- 🌐 Frontend: http://localhost:5000

## 📁 Project Structure

```
.
├── api_server.py              # FastAPI ML backend
├── requirements.txt           # Python dependencies
├── data/
│   └── weather_cleaned.csv    # Training data
├── Frontend/
│   ├── client/                # React frontend
│   │   └── src/
│   │       └── pages/
│   │           └── weather.tsx  # Weather prediction page
│   ├── server/                # Express backend
│   │   ├── index.ts           # Server entry point
│   │   └── routes.ts          # API routes (proxy to FastAPI)
│   └── shared/
│       └── schema.ts          # TypeScript types
└── README_INTEGRATION.md      # This file
```

## 🔌 API Endpoints

### FastAPI Backend (Port 8000)

#### `GET /`
Health check and model metrics
```json
{
  "status": "online",
  "model": "XGBoost",
  "metrics": {
    "accuracy": 0.85,
    "precision": 0.82,
    "recall": 0.73,
    "f1_score": 0.77
  }
}
```

#### `GET /predict`
Get rain prediction for a specific location and date

**Parameters:**
- `lat` (float): Latitude (-90 to 90)
- `lon` (float): Longitude (-180 to 180)
- `day` (int): Day of month (1-31)
- `month` (int): Month (1-12)
- `year` (int): Year

**Example:**
```
GET /predict?lat=30.0444&lon=31.2357&day=15&month=6&year=2024
```

**Response:**
```json
{
  "rain_probability": 0.65,
  "rain_predicted": 1,
  "season": "Summer",
  "season_code": 2,
  "confidence": 0.30,
  "location": {
    "latitude": 30.0444,
    "longitude": 31.2357
  },
  "date": {
    "day": 15,
    "month": 6,
    "year": 2024
  },
  "model_info": {
    "threshold": 0.50,
    "model_accuracy": 0.85
  }
}
```

#### `GET /model-info`
Get detailed model information

### Express Backend (Port 5000)

#### `GET /api/predict`
Proxy endpoint to FastAPI `/predict`

#### `GET /api/ml-status`
Check if ML backend is connected

#### `GET /api/model-info`
Proxy endpoint to FastAPI `/model-info`

## 🎨 Frontend Features

- **Interactive Map**: Click to select location coordinates
- **Form Input**: Manual coordinate entry with validation
- **Real-time Prediction**: Get ML-powered rain predictions
- **Visual Results**: Beautiful card-based results display with:
  - Rain probability percentage
  - Binary prediction (Rain/No Rain)
  - Season information
  - Confidence score
  - Model accuracy

## 🛠️ Development

### Running in Development Mode

**Terminal 1 - FastAPI:**
```powershell
.\venv\Scripts\Activate.ps1
python api_server.py
```

**Terminal 2 - Frontend:**
```powershell
cd Frontend
npm run dev
```

### Building for Production

```powershell
cd Frontend
npm run build
npm run start:prod
```

## 🧪 Testing the Integration

1. **Check ML Backend Status:**
   ```powershell
   curl http://localhost:8000
   ```

2. **Test Prediction Endpoint:**
   ```powershell
   curl "http://localhost:8000/predict?lat=30&lon=31&day=15&month=6&year=2024"
   ```

3. **Test via Frontend:**
   - Open http://localhost:5000/weather
   - Click on the map or enter coordinates
   - Select a date
   - Click "Get Weather Prediction"

## 🔧 Troubleshooting

### ML Backend Not Starting

**Issue:** ImportError for packages
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Issue:** CSV file not found
```
# Ensure weather_cleaned.csv is in the data/ folder
```

### Frontend Can't Connect to ML Backend

**Issue:** ML Backend status shows "offline"

1. Ensure FastAPI is running on port 8000
2. Check terminal for FastAPI errors
3. Verify CORS is enabled in `api_server.py`

### Port Already in Use

**FastAPI (8000):**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process (replace PID)
taskkill /PID <PID> /F
```

**Express (5000):**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000
# Kill the process
taskkill /PID <PID> /F
```

## 📊 Model Information

- **Algorithm:** XGBoost Classifier
- **Features:** Season (derived from month)
- **Training:** SMOTE for handling imbalanced data
- **Optimization:** Threshold tuning for balanced Recall/Precision
- **Metrics:** ~85% accuracy, ~82% precision, ~73% recall

## 🌟 Features

✅ Real-time ML predictions  
✅ Interactive map selection  
✅ Season-based weather modeling  
✅ Beautiful UI with Tailwind CSS  
✅ Type-safe TypeScript frontend  
✅ RESTful API design  
✅ Comprehensive error handling  
✅ Model performance metrics display  

## 📝 Notes

- The model currently uses **season** as the primary feature
- Location coordinates (lat/lon) are captured but not used in the current model
- To improve predictions, consider adding more features like:
  - Historical weather data for the location
  - Elevation
  - Proximity to water bodies
  - Climate zone classification

## 🤝 Contributing

1. Ensure both servers are running
2. Make changes to either backend or frontend
3. Test the integration thoroughly
4. Check for TypeScript errors: `npm run check`

## 📄 License

MIT

---

**Built with:** FastAPI • React • TypeScript • XGBoost • Tailwind CSS
