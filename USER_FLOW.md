# 🎯 User Flow Guide

## Complete User Journey

### 1️⃣ Startup Phase

```
Developer starts application
         │
         ├─ Terminal 1: python api_server.py
         │  └─ ✓ FastAPI starts on port 8000
         │  └─ ✓ XGBoost model loaded
         │  └─ ✓ Training metrics displayed
         │
         └─ Terminal 2: npm run dev (in Frontend/)
            └─ ✓ Vite dev server starts on port 5000
            └─ ✓ Express backend ready
            └─ ✓ Frontend accessible
```

### 2️⃣ User Arrival

```
User opens browser
         │
         ▼
http://localhost:5000
         │
         ▼
Landing Page (home.tsx)
         │
         ├─ Beautiful space-themed design
         ├─ NASA branding
         └─ "Weather Prediction Portal" link
              │
              ▼
        Click to continue
```

### 3️⃣ Weather Prediction Page

```
User arrives at /weather
         │
         ▼
┌─────────────────────────────────────┐
│  Weather Prediction Portal          │
│                                     │
│  🟢 ML Backend: Online              │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Left Side          │  Right Side    │
│  ─────────          │  ──────────    │
│  • Coordinate Form  │  • Interactive │
│  • Date Selector    │    Map         │
│  • Submit Button    │                │
└─────────────────────────────────────┘
```

### 4️⃣ Location Selection

#### Option A: Click on Map

```
User clicks map at specific point
         │
         ▼
Map captures coordinates
         │
         ├─ Latitude: 30.0444
         ├─ Longitude: 31.2357
         │
         ▼
Form fields auto-populate
         │
         ▼
Selected Location shows:
"Lat: 30.0444, Lng: 31.2357"
```

#### Option B: Manual Entry

```
User types coordinates manually
         │
         ├─ Latitude: 30.0444
         ├─ Longitude: 31.2357
         │
         ▼
Validation occurs (Zod schema)
         │
         ├─ Lat must be -90 to 90
         ├─ Lon must be -180 to 180
         │
         ▼
✓ Valid coordinates accepted
```

### 5️⃣ Date Selection

```
User clicks date picker
         │
         ▼
Calendar appears
         │
         ├─ Default: Today's date
         └─ User selects: 2024-06-15
              │
              ▼
        Date saved in form
```

### 6️⃣ Prediction Request

```
User clicks "Get Weather Prediction"
         │
         ▼
Frontend validation
         │
         ├─ Check: Coordinates valid?
         ├─ Check: Date valid?
         ├─ Check: ML backend online?
         │
         ▼
✓ All checks pass
         │
         ▼
Button shows loading state
         │
         ├─ 🔄 "Processing..."
         ├─ Spinner animation
         │
         ▼
Form data prepared:
         │
         ├─ Parse date: "2024-06-15"
         ├─ Day: 15
         ├─ Month: 6
         ├─ Year: 2024
         │
         ▼
API Request sent:
GET /api/predict?lat=30.0444&lon=31.2357&day=15&month=6&year=2024
```

### 7️⃣ Backend Processing

```
Express receives request
         │
         ▼
Proxy to FastAPI
         │
         ▼
FastAPI processes
         │
         ├─ Month 6 → Season 2 (Summer)
         ├─ Create feature: {SEASON: 2}
         ├─ XGBoost prediction
         ├─ Probability: 0.65
         ├─ Apply threshold: 0.50
         ├─ Result: 1 (Rain predicted)
         │
         ▼
Response generated:
{
  "rain_probability": 0.65,
  "rain_predicted": 1,
  "season": "Summer",
  "confidence": 0.30,
  ...
}
         │
         ▼
Express proxies back
         │
         ▼
Frontend receives response
```

### 8️⃣ Results Display

```
Frontend processes response
         │
         ▼
┌─────────────────────────────────────┐
│  🌧️  Prediction Results              │
│  ─────────────────────────────────  │
│                                     │
│  ┌─────────────────────────────┐   │
│  │    Rain Expected             │   │
│  │    65.0% probability         │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌──────────┬──────────┐           │
│  │ Season   │ Confidence│           │
│  │ ☀️ Summer │ 30.0%    │           │
│  └──────────┴──────────┘           │
│                                     │
│  Location: 30.0444°, 31.2357°      │
│                                     │
│  Model Threshold: 0.50              │
│  Model Accuracy: 85.0%              │
└─────────────────────────────────────┘
         │
         ▼
Toast notification appears:
"Prediction Complete ✓
High chance of rain (65.0%)"
```

### 9️⃣ User Actions After Prediction

#### Option 1: New Prediction
```
User clicks map at new location
         │
         ▼
Previous results cleared
         │
         ▼
New prediction flow starts
```

#### Option 2: Change Date
```
User selects different date
         │
         ▼
Submit new prediction
         │
         ▼
New results display
```

#### Option 3: View Details
```
User examines results card
         │
         ├─ Rain probability
         ├─ Season information
         ├─ Confidence level
         ├─ Model accuracy
         │
         ▼
User understands weather forecast
```

## 🎨 Visual States

### State 1: Initial Load
```
┌─────────────────────────────────────┐
│  Weather Prediction Portal          │
│  🔄 ML Backend: Checking...         │
│                                     │
│  Form: Empty                        │
│  Map: No selection                  │
│  Results: None                      │
└─────────────────────────────────────┘
```

### State 2: Backend Connected
```
┌─────────────────────────────────────┐
│  Weather Prediction Portal          │
│  🟢 ML Backend: Online              │
│                                     │
│  Form: Ready for input              │
│  Map: Interactive                   │
│  Results: None                      │
└─────────────────────────────────────┘
```

### State 3: Location Selected
```
┌─────────────────────────────────────┐
│  Weather Prediction Portal          │
│  🟢 ML Backend: Online              │
│                                     │
│  Form: Coordinates filled           │
│  Map: 📍 Pin at location           │
│  Results: None                      │
│  Button: Enabled                    │
└─────────────────────────────────────┘
```

### State 4: Processing
```
┌─────────────────────────────────────┐
│  Weather Prediction Portal          │
│  🟢 ML Backend: Online              │
│                                     │
│  Form: Locked                       │
│  Map: Disabled                      │
│  Results: None                      │
│  Button: 🔄 Processing...          │
└─────────────────────────────────────┘
```

### State 5: Results Displayed
```
┌─────────────────────────────────────┐
│  Weather Prediction Portal          │
│  🟢 ML Backend: Online              │
│                                     │
│  Form: Editable                     │
│  Map: Interactive                   │
│  Results: 🌧️ Rain Expected (65%)   │
│  Button: Enabled                    │
└─────────────────────────────────────┘
```

### State 6: Backend Offline
```
┌─────────────────────────────────────┐
│  Weather Prediction Portal          │
│  🔴 ML Backend: Offline             │
│                                     │
│  Form: Editable                     │
│  Map: Interactive                   │
│  Results: None                      │
│  Button: Disabled                   │
│  Error: "Please start ML backend"   │
└─────────────────────────────────────┘
```

## 🔄 Error Handling Flow

### Error Scenario 1: ML Backend Down
```
User submits prediction
         │
         ▼
Frontend checks backend status
         │
         ▼
❌ Backend offline detected
         │
         ▼
Button remains disabled
         │
         ▼
Error toast: "ML backend not available"
```

### Error Scenario 2: Invalid Coordinates
```
User enters invalid data
         │
         ├─ Latitude: 150 (> 90)
         └─ Longitude: -200 (< -180)
              │
              ▼
        Zod validation fails
              │
              ▼
Red error text appears under fields
              │
              ▼
Submit button disabled
```

### Error Scenario 3: Network Error
```
API request sent
         │
         ▼
Network timeout
         │
         ▼
Fetch error caught
         │
         ▼
Toast: "Failed to get prediction"
         │
         ▼
Results cleared
         │
         ▼
User can retry
```

## 📱 Responsive Behavior

### Desktop (1280px+)
```
┌────────────────────────────────────────────┐
│  Header                                    │
│  ─────────────────────────────────────────│
│  ┌──────────────┬──────────────────────┐  │
│  │ Form & Input │ Interactive Map      │  │
│  │              │                      │  │
│  │ Results Card │                      │  │
│  └──────────────┴──────────────────────┘  │
│  NASA Data Sources                         │
└────────────────────────────────────────────┘
```

### Tablet (768px - 1279px)
```
┌──────────────────────────┐
│  Header                  │
│  ───────────────────────│
│  ┌────────┬──────────┐  │
│  │ Form   │ Map      │  │
│  │        │          │  │
│  └────────┴──────────┘  │
│  ┌──────────────────┐   │
│  │ Results Card     │   │
│  └──────────────────┘   │
│  NASA Data Sources      │
└──────────────────────────┘
```

### Mobile (< 768px)
```
┌────────────────┐
│  Header        │
│  ─────────────│
│  ┌──────────┐ │
│  │ Form     │ │
│  └──────────┘ │
│  ┌──────────┐ │
│  │ Map      │ │
│  └──────────┘ │
│  ┌──────────┐ │
│  │ Results  │ │
│  └──────────┘ │
│  Data Sources │
└────────────────┘
```

## 🎯 Success Metrics

### User completes prediction successfully when:
✅ Map location selected or coordinates entered  
✅ Date chosen  
✅ Backend status is online  
✅ Prediction request processed  
✅ Results display within 1-2 seconds  
✅ Clear rain/no-rain indication shown  
✅ User understands the prediction  

---

**This integration provides a seamless, intuitive weather prediction experience powered by machine learning!** 🌤️
