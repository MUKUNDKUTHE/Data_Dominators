# backend/services/llm_service.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# CLIENT SETUP
# OpenAI SDK pointed at Groq's endpoint
# To switch providers: change .env only
# ─────────────────────────────────────────
client = OpenAI(
    api_key  = os.getenv("GROQ_API_KEY"),
    base_url = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
)

LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
}

BASE_RULES = """- Be direct and specific (use actual dates, prices, market names)
- Always explain WHY you made each recommendation
- Keep responses concise and under 150 words
- Never use technical jargon
- Be encouraging and trustworthy
- CRITICAL: Use ONLY the EXACT price numbers given to you. NEVER invent, round, or alter any price, distance, or number. Copy them exactly as provided.
- CRITICAL: Start your response DIRECTLY with '1.' \u2014 NO greeting, NO intro sentence, NO preamble. The very first character must be '1'."""


def _build_system_prompt(language: str = "en") -> str:
    lang_name = LANGUAGE_NAMES.get(language, "English")
    if language == "en":
        lang_rule = "- Always respond in simple, clear English"
    else:
        lang_rule = (
            f"- CRITICAL: You MUST respond entirely in {lang_name}. "
            f"Every single word of all 4 points must be written in {lang_name} script. "
            "Do NOT use English except for numbers, proper nouns (place names, crop names), and units."
        )
    return f"""You are AgriChain, an AI assistant helping Indian farmers make better harvest and selling decisions.
{lang_rule}
{BASE_RULES}"""


# ─────────────────────────────────────────
# FUNCTION 1 — GENERATE RECOMMENDATION
# Main function called by recommend.py route
# ─────────────────────────────────────────
def generate_recommendation(context: dict, language: str = "en") -> str:
    """
    Generates plain language harvest + market recommendation.
    Loads prompt from harvest_prompt.txt and fills in context.
    Responds in the given language (en/hi/mr/te/ta/kn).
    """
    prompt = _build_prompt("harvest_prompt.txt", context)

    try:
        response = client.chat.completions.create(
            model    = LLM_MODEL,
            messages = [
                {"role": "system", "content": _build_system_prompt(language)},
                {"role": "user",   "content": prompt}
            ],
            temperature = 0.3,
            max_tokens  = 300
        )
        text = response.choices[0].message.content
        # Sanitize: replace ₹ symbol with Rs. to avoid encoding issues in transit
        text = text.replace('\u20b9', 'Rs.').replace('â\x82¹', 'Rs.').replace('â‚¹', 'Rs.')
        return text

    except Exception as e:
        # Fallback — rule-based plain text if LLM fails
        return _fallback_recommendation(context)


# ─────────────────────────────────────────
# FUNCTION 2 — GENERATE SPOILAGE ADVICE
# Called by spoilage.py route
# ─────────────────────────────────────────
def generate_spoilage_advice(context: dict) -> str:
    """
    Generates plain language spoilage risk advice.
    Loads prompt from spoilage_prompt.txt and fills in context.
    """
    prompt = _build_prompt("spoilage_prompt.txt", context)

    try:
        response = client.chat.completions.create(
            model    = LLM_MODEL,
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are AgriChain. Give practical, affordable preservation "
                        "advice to Indian farmers with limited resources. "
                        "Always rank actions cheapest first. Keep under 120 words."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature = 0.3,
            max_tokens  = 200
        )
        return response.choices[0].message.content

    except Exception as e:
        return _fallback_spoilage(context)


# ─────────────────────────────────────────
# HELPER — BUILD PROMPT FROM FILE
# ─────────────────────────────────────────
def _build_prompt(filename: str, context: dict) -> str:
    """
    Loads prompt template from prompts/ folder
    and fills in context values.
    Falls back to inline prompt if file missing.
    """
    BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
    PROMPTS_DIR  = os.path.join(BASE_DIR, "../prompt")
    prompt_path  = os.path.join(PROMPTS_DIR, filename)

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()
        return template.format(**context)
    except FileNotFoundError:
        # Fallback inline prompt
        return _inline_prompt(filename, context)
    except KeyError as e:
        # Missing key in context — use what we have
        print(f"⚠️ Prompt key missing: {e}. Using partial context.")
        return _inline_prompt(filename, context)


def _inline_prompt(filename: str, context: dict) -> str:
    """Fallback inline prompts if files not found."""
    if "harvest" in filename:
        return f"""
        Farmer's crop    : {context.get('crop', 'Unknown')}
        Location         : {context.get('district', '')}, {context.get('state', '')}
        Predicted price  : ₹{context.get('predicted_price', 'N/A')}/quintal
        Price trend      : {context.get('price_trend', 'stable')}
        Best market      : {context.get('best_market', 'local market')}
        Harvest window   : {context.get('harvest_window', 'this week')}
        Weather          : {context.get('weather', 'normal')}
        Spoilage risk    : {context.get('spoilage_risk', 'Low')}
        Days safe        : {context.get('days_safe', 7)} days

        Give the farmer: WHEN to harvest, WHERE to sell, WHAT price to expect,
        and ONE urgent action. Explain WHY. Under 150 words.
        """
    else:
        return f"""
        Crop         : {context.get('crop', 'Unknown')}
        Storage      : {context.get('storage_type', 'basic_shed')}
        Transit      : {context.get('transit_hours', 6)} hours
        Temperature  : {context.get('temperature', '30°C')}
        Humidity     : {context.get('humidity', '65%')}
        Risk score   : {context.get('spoilage_score', 50)}/100

        Give: risk level, days safe, top 3 cheapest preservation actions.
        Under 120 words.
        """


# ─────────────────────────────────────────
# FALLBACK — Rule-based output if LLM fails
# Ensures demo never crashes
# ─────────────────────────────────────────
def _fallback_recommendation(context: dict) -> str:
    crop         = context.get("crop", "your crop")
    best_market  = context.get("best_market", "nearest market")
    price        = context.get("predicted_price", "N/A")
    trend        = context.get("price_trend", "stable")
    spoilage     = context.get("spoilage_risk", "Low")
    days         = context.get("days_safe", 7)
    harvest_day  = context.get("best_harvest_day", "soon")

    msg = (
        f"Harvest {crop} around {harvest_day} when weather conditions are best. "
        f"Sell at {best_market} where prices average ₹{price}/quintal. "
        f"Price trend is currently {trend}. "
    )
    if spoilage in ["Medium", "High"]:
        msg += (f"⚠️ {spoilage} spoilage risk — sell within {days} days. "
                f"Store in shade and improve ventilation immediately.")
    else:
        msg += f"Low spoilage risk — you have {days} days to sell comfortably."

    return msg


def _fallback_spoilage(context: dict) -> str:
    crop  = context.get("crop", "your crop")
    score = context.get("spoilage_score", 50)
    risk  = "High" if score >= 65 else "Medium" if score >= 35 else "Low"
    return (
        f"{risk} spoilage risk for {crop} (score: {score}/100). "
        f"Actions: 1) Sort damaged produce (Free) "
        f"2) Move to shade (Free) "
        f"3) Use jute sacks (₹5-10/bag)"
    )