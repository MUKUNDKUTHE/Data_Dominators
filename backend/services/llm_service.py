# backend/services/llm_service.py

import os
from openai import OpenAI

# Groq is OpenAI-compatible — just swap base_url
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

LLM_MODEL = "llama-3.3-70b-versatile"


def generate_recommendation(context: dict) -> str:
    """
    Takes structured outputs from all models and returns
    a plain-language farmer-friendly recommendation.
    """
    prompt = build_prompt(context)

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are AgriChain, an AI assistant helping Indian farmers "
                    "make better harvest and selling decisions. "
                    "Always respond in simple, clear English. "
                    "Be direct, specific, and trustworthy. "
                    "Always explain WHY you made each recommendation. "
                    "Keep responses under 150 words."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=300
    )

    return response.choices[0].message.content


def generate_spoilage_advice(context: dict) -> str:
    """
    Generates spoilage risk explanation and ranked preservation actions.
    """
    prompt = f"""
    Crop: {context['crop']}
    Storage type: {context['storage_type']}
    Transit time: {context['transit_hours']} hours
    Temperature: {context['temperature']}
    Humidity: {context['humidity']}
    Spoilage risk score: {context['spoilage_score']}/100

    Give the farmer:
    1. Spoilage risk level (Low / Medium / High)
    2. Why this risk exists (1 sentence)
    3. Top 3 preservation actions ranked cheapest first
    """

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are AgriChain. Give practical, affordable preservation "
                    "advice to Indian farmers with limited resources. "
                    "Always rank actions cheapest first."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=200
    )

    return response.choices[0].message.content


def build_prompt(context: dict) -> str:
    """Loads prompt template and fills context values."""
    try:
        with open("prompts/harvest_prompt.txt", "r") as f:
            template = f.read()
        return template.format(**context)
    except FileNotFoundError:
        return f"""
        Crop: {context.get('crop')}
        Location: {context.get('state')}
        Predicted price: ₹{context.get('predicted_price')}/quintal
        Price trend: {context.get('price_trend')}
        Best market: {context.get('best_market')}
        Harvest window: {context.get('harvest_window')}
        Weather: {context.get('weather')}
        Spoilage risk: {context.get('spoilage_risk')}
        Preservation actions: {context.get('preservation_actions')}

        Give the farmer a clear recommendation.
        Tell them WHEN to harvest, WHERE to sell, and WHY.
        Mention spoilage risk if Medium or High.
        """