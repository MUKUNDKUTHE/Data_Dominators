# 🌾 AgriChain — Farm-to-Market Intelligence Platform

> Helping Indian farmers harvest at the right time, sell at the right place.

## Problem
India's farmers lose up to 40% of produce value due to poor harvest timing and market mismatch — not poor farming. AgriChain fixes this with AI.

## What It Does
- **Harvest Window Recommendation** — optimal harvest dates based on crop maturity, weather forecast, and soil conditions
- **Best Market Suggestion** — top mandis ranked by expected price with distance-adjusted recommendations
- **Spoilage Risk Assessment** — post-harvest risk scoring based on storage and transit time
- **Preservation Tips** — ranked by cost and effectiveness for small farmers
- **Plain Language Output** — designed for farmers with basic Android phones, no data literacy required
- **Explainable AI** — every recommendation comes with a clear reason, not just a result

## Tech Stack
- **Backend:** Python, Flask, Claude API (Anthropic)
- **Frontend:** HTML, CSS, JavaScript
- **Data:** Agmarknet mandi prices, OpenWeatherMap API
- **AI:** Claude Sonnet for reasoning and plain language generation

## Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
python app.py
```

### Frontend
Open `frontend/index.html` in browser or serve with any static server.

## API Endpoints
- `POST /api/recommend` — harvest window + market recommendation
- `POST /api/spoilage` — spoilage risk + preservation tips

## Data Sources
- Mandi Prices: data.gov.in / Agmarknet
- Weather: OpenWeatherMap API
- Soil Profiles: Static reference data based on ICAR guidelines