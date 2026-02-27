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
| 📊 **Price Prediction** | CatBoost ML model trained on Agmarknet mandi data |
| 🚚 **Transit Intelligence** | Real routing via OLA Maps with Haversine sanity-check fallback |

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
│   │   └── spoilage.py         # /api/spoilage
│   ├── services/
│   │   ├── llm_service.py      # Groq LLM, multilingual system prompt
│   │   ├── mandi_service.py    # Price prediction + best market
│   │   ├── weather_service.py  # OpenWeather, parallel fetch, geocoding
│   │   ├── crop_service.py     # Spoilage scoring, soil suitability
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
       ├── pages/              # HomePage, RecommendPage, ResultsPage, ...
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
Set `transit_hours: 0` to auto-calculate via OLA Maps. Set `language` to `en | hi | mr | te | ta | kn` to get the AI recommendation in that language.

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
Farmer knows: when to harvest, where to sell, what price to expect, what to do today
```

