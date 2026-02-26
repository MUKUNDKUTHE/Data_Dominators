# backend/app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.recommend import router as recommend_router
from routes.spoilage import router as spoilage_router


# APP SETUP

app = FastAPI(
    title       = "AgriChain API",
    description = "AI-powered farm-to-market recommendation system for Indian farmers",
    version     = "1.0.0"
)


# CORS — allows frontend to call the API

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],   # tighten in production
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


# ROUTES

app.include_router(recommend_router, prefix="/api")
app.include_router(spoilage_router,  prefix="/api")



# HEALTH CHECK

@app.get("/")
def root():
    return {
        "status":  "AgriChain API is running",
        "version": "1.0.0",
        "routes": {
            "recommend": "/api/recommend",
            "spoilage":  "/api/spoilage",
            "health":    "/api/health"
        }
    }


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "AgriChain"}



# RUN
# uvicorn app:app --reload --port 8000

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)