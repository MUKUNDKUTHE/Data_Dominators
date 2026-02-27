# 🌾 AgriChain — Farm-to-Market Intelligence Platform

> Helping Indian farmers harvest at the right time, sell at the right place.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript)](https://typescriptlang.org)

---

## Problem

India's farmers lose up to **40% of produce value** due to poor harvest timing and market mismatch — not poor farming. AgriChain fixes this with AI-driven intelligence delivered in the farmer's own language, on a basic Android phone.

---

## What It Does

| Feature | Description |
|---|---|
| 🗓️ **Harvest Window** | Optimal harvest dates based on crop maturity, weather forecast, and soil conditions |
| 🏪 **Best Market Finder** | Top mandis ranked by expected price with OLA Maps-powered distance routing |
| ⚠️ **Spoilage Risk Score** | Post-harvest risk scoring based on storage type, transit time, and weather |
| 🌿 **Preservation Tips** | Actionable, cost-ranked preservation actions for small farmers |
| 🤖 **AI Recommendation** | 4-point plain-language advice from Groq LLM (Llama 3.3 70B) |
| 🗣️ **Voice Input** | Web Speech API for hands-free crop/location entry in all 6 languages |
| 🌐 **6 Languages** | English, हिंदी, मराठी, తెలుగు, தமிழ், ಕನ್ನಡ — UI and AI output both localized |
| 📊 **Price Prediction** | CatBoost ML model trained on 880K+ rows of Agmarknet mandi data |
| 🚚 **Transit Intelligence** | Real routing via OLA Maps with Haversine sanity-check fallback |
| 📈 **Arrival Surge Prediction** | Detects upcoming high-supply weeks from historical data; shows real date ranges and price impact % so farmers can time their sale before the glut |
| 🛡️ **Loss Insurance Estimator** | Calculates value-at-risk, expected crop loss, storage upgrade cost, loss saved, and ROI — helps farmers decide if cold storage investment is worth it |
| 🤝 **Middleman Bypass Score** | Scores 0–10 opportunity to sell direct (FPO / e-NAM / buyer network), estimates commission saved in ₹ |

---

## Tech Stack

### Backend
| Layer | Technology |
|---|---|
| API Framework | FastAPI 0.111 + Uvicorn |
| ML Model | CatBoost (mandi price prediction) |
| LLM | Groq API — `llama-3.3-70b-versatile` via OpenAI SDK |
| Routing | OLA Maps SDK (`py-olamaps`) + Haversine fallback |
| Weather | OpenWeatherMap API (parallel fetch, 10-min cache) |
| Geocoding | OpenWeatherMap Geo API |

### Frontend
| Layer | Technology |
|---|---|
| Framework | React 18 + TypeScript + Vite |
| Styling | Tailwind CSS + shadcn/ui |
| Animation | Framer Motion |
| Icons | Lucide React |
| Voice | Web Speech API (all 6 Indian language variants) |

### Mobile
| Layer | Technology |
|---|---|
| Framework | Expo (React Native) |
| Wrapper | WebView pointing to web frontend |

---

## Project Structure

```
AgriChain/
├── backend/
│   ├── app.py                  # FastAPI entry point
│   ├── routes/
│   │   ├── recommend.py        # /api/recommend, /api/transit, /api/price
│   │   ├── spoilage.py         # /api/spoilage
│   │   └── insights.py         # /api/arrival-prediction, /api/loss-risk, /api/bypass-score
│   ├── services/
│   │   ├── llm_service.py      # Groq LLM, multilingual system prompt
│   │   ├── mandi_service.py    # Price prediction + best market + arrival surge + bypass score
│   │   ├── weather_service.py  # OpenWeather, parallel fetch, geocoding
│   │   ├── crop_service.py     # Spoilage scoring, soil suitability, loss insurance
│   │   └── explainability_service.py
│   ├── models/
│   │   └── agrichain_price_model.cbm  # Trained CatBoost model
│   ├── data/
│   │   ├── processed/mandi_prices.csv
│   │   └── raw/                # Agmarknet source CSVs
│   └── prompt/
│       ├── harvest_prompt.txt
│       └── spoilage_prompt.txt
├── frontend/
   └── src/
       ├── pages/              # HomePage, RecommendPage, ResultsPage, SpoilagePage, InsightsPage
       ├── components/         # VoiceInput, SpoilageGauge, BottomNav, ...
       ├── lib/
       │   ├── i18n.ts         # 6-language translations
       │   ├── api.ts          # Typed API client
       │   └── data.ts         # Crops, states, storage types
       └── contexts/
           └── LanguageContext.tsx

```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- API keys: `GROQ_API_KEY`, `OPENWEATHER_API_KEY`, `OLA_MAPS_API_KEY`

### 1 — Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r ../requirements.txt
copy .env.example .env         # then fill in your API keys
python app.py
```

Backend runs at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

### 2 — Web Frontend

```bash
cd frontend
npm install
# create .env with:
# VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

Frontend runs at `http://localhost:5173`


---

## Environment Variables

### Backend `.env`
```env
GROQ_API_KEY=your_groq_key
OPENWEATHER_API_KEY=your_openweather_key
OLA_MAPS_API_KEY=your_ola_maps_key
LLM_MODEL=llama-3.3-70b-versatile
LLM_BASE_URL=https://api.groq.com/openai/v1
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/recommend` | Full recommendation: price + weather + transit + LLM advice |
| `POST` | `/api/spoilage` | Spoilage risk score + preservation actions |
| `GET` | `/api/transit` | Driving time between farmer location and market |
| `GET` | `/api/price` | Quick mandi price lookup |
| `GET` | `/api/crops` | List of supported crops |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/arrival-prediction` | Arrival surge prediction — upcoming high-supply weeks + best-sell windows |
| `POST` | `/api/loss-risk` | Loss insurance — value at risk, expected loss, upgrade ROI |
| `POST` | `/api/bypass-score` | Middleman bypass score — direct-sell opportunity + commission savings |

### `POST /api/recommend` — key fields
```json
{
  "crop": "Tomato",
  "state": "Maharashtra",
  "district": "Pune",
  "market": "Nagpur",
  "harvest_date": "2026-03-07",
  "storage_type": "basic_shed",
  "transit_hours": 0,
  "language": "hi"
}
```
Set `transit_hours: 0` to auto-calculate via OLA Maps. Set `language` to `en | hi | mr | te | ta | kn`.

### `POST /api/arrival-prediction`
```json
{ "crop": "Tomato", "state": "Maharashtra", "date": "2026-03-01" }
```
Returns `alert`, `advice`, `upcoming_surges` (with calendar date ranges and price impact %), and `best_price_weeks`.

### `POST /api/loss-risk`
```json
{
  "crop": "Tomato",
  "quantity_quintals": 10,
  "predicted_price": 1500,
  "spoilage_score": 35,
  "storage_type": "basic_shed"
}
```
Returns `value_at_risk`, `expected_loss`, `upgrade_cost`, `loss_saved`, `roi`, `urgency`, `upgrade_tip`, `summary`.

### `POST /api/bypass-score`
```json
{
  "crop": "Tomato",
  "state": "Maharashtra",
  "quantity_quintals": 10,
  "predicted_price": 1500,
  "price_trend": "stable"
}
```
Returns `bypass_score` (0–10), `verdict`, `commission_saved` (₹), `commission_rate_pct`, `reasons`, `next_step`.

---


## Data Sources

| Data | Source |
|---|---|
| Mandi Prices | [data.gov.in](https://data.gov.in) / Agmarknet |
| Weather & Geocoding | OpenWeatherMap API |
| Road Routing | OLA Maps Directions API |
| Soil Profiles | ICAR-based static reference data |

---

## Key Technical Decisions

- **Haversine sanity check** on OLA Maps results — if returned road distance is < 70% of straight-line distance, the route is rejected and a physics-based estimate (×1.35 road factor, 50 km/h) is used instead.
- **Multilingual LLM** — system prompt dynamically instructs the model to respond in the selected language; the prompt file avoids any hardcoded language instruction.
- **Parallel weather fetch** — `ThreadPoolExecutor` fetches current conditions and forecast simultaneously with a 10-minute in-memory cache.
- **Voice input** uses BCP-47 Indian regional variants (`hi-IN`, `mr-IN`, `te-IN`, `ta-IN`, `kn-IN`) for best accuracy on Indian crop and place names.
- **Arrival surge detection** scans 880K+ rows of historical mandi data, computes per-week mean arrival volumes, flags weeks with >1.5× average as surges, and maps ISO week numbers to human-readable date ranges.
- **Loss insurance ROI** compares expected loss at current storage vs loss after upgrade, dividing savings by upgrade cost — if ROI > 1 the upgrade pays for itself this season.
- **Bypass score** is a 0–10 composite of quantity threshold (FPO min), price trend stability, network density by state, and commission savings relative to crop value.

---

## Problem → Solution

```
Farmer has crop ready
        ↓
Opens AgriChain (speaks in Hindi/Marathi/etc.)
        ↓
System checks: mandi prices + weather + soil + transit distance
        ↓
CatBoost predicts price at local & best market
        ↓
Groq LLM generates 4-point advice in farmer's language
        ↓
Insights tab: arrival surge dates · bypass score · loss insurance ROI
        ↓
Farmer knows: when to harvest, where to sell, what price to expect,
             whether to upgrade storage, and if going direct saves money
```

