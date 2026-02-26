# backend/services/crop_profiles.py
#
# Standalone crop profiles data file
# Imported by crop_service.py
#
# Contains:
#   CROP_PROFILES         → shelf life, storage data for 77 crops
#   CROP_TO_DATASET_MAP   → maps mandi crops to ML model's 10 known crops
#
# Based on ICAR + FAO post-harvest storage guidelines
# To add a new crop: just add a new entry to CROP_PROFILES




# CROP PROFILES
# 77 crops covering all major Indian mandis
#
# Fields:
#   shelf_life_days : days at ideal conditions
#   ideal_temp      : °C optimal storage temperature
#   ideal_humidity  : % optimal relative humidity
#   storage_tip     : plain language farmer advice
#   spoilage_notes  : urgency note for farmer


CROP_PROFILES = {

    # ── Vegetables — Highly Perishable (1-7 days) ──
    "Tomato": {
        "shelf_life_days": 7,   "ideal_temp": 13, "ideal_humidity": 90,
        "storage_tip":    "Store at 13°C. Never refrigerate below 10°C — causes chilling injury.",
        "spoilage_notes": "Highly perishable. Sell within 5-7 days. Avoid stacking."
    },
    "Spinach": {
        "shelf_life_days": 3,   "ideal_temp": 0,  "ideal_humidity": 95,
        "storage_tip":    "Keep moist and cool. Store in perforated bags.",
        "spoilage_notes": "Extremely perishable. Sell within 2-3 days."
    },
    "Coriander": {
        "shelf_life_days": 3,   "ideal_temp": 0,  "ideal_humidity": 95,
        "storage_tip":    "Stand stems in water like flowers. Keep cool and moist.",
        "spoilage_notes": "Very perishable. Sell same day or next day."
    },
    "Fenugreek": {
        "shelf_life_days": 3,   "ideal_temp": 0,  "ideal_humidity": 95,
        "storage_tip":    "Keep moist and cool in shade. Bundle loosely.",
        "spoilage_notes": "Very perishable. Wilts quickly in heat."
    },
    "Bitter Gourd": {
        "shelf_life_days": 5,   "ideal_temp": 12, "ideal_humidity": 85,
        "storage_tip":    "Store at 12°C. Avoid chilling below 10°C.",
        "spoilage_notes": "Moderate perishability. Sell within 5 days."
    },
    "Bottle Gourd": {
        "shelf_life_days": 14,  "ideal_temp": 10, "ideal_humidity": 85,
        "storage_tip":    "Store whole in cool area. Do not cut before selling.",
        "spoilage_notes": "Good shelf life when stored whole."
    },
    "Ridge Gourd": {
        "shelf_life_days": 5,   "ideal_temp": 10, "ideal_humidity": 85,
        "storage_tip":    "Store in cool, humid conditions. Avoid bruising.",
        "spoilage_notes": "Moderate perishability. Sell within 5 days."
    },
    "Snake Gourd": {
        "shelf_life_days": 5,   "ideal_temp": 10, "ideal_humidity": 85,
        "storage_tip":    "Handle carefully — skin damages easily.",
        "spoilage_notes": "Moderate perishability."
    },
    "Eggplant": {
        "shelf_life_days": 7,   "ideal_temp": 10, "ideal_humidity": 90,
        "storage_tip":    "Store at 10-12°C. Chilling injury below 10°C causes brown spots.",
        "spoilage_notes": "Perishable. Sensitive to cold damage and bruising."
    },
    "Okra": {
        "shelf_life_days": 5,   "ideal_temp": 7,  "ideal_humidity": 90,
        "storage_tip":    "Store at 7-10°C. Chilling sensitive below 7°C.",
        "spoilage_notes": "Perishable. Loses quality quickly above 10°C."
    },
    "Capsicum": {
        "shelf_life_days": 14,  "ideal_temp": 7,  "ideal_humidity": 90,
        "storage_tip":    "Store at 7-10°C in humid conditions.",
        "spoilage_notes": "Moderate shelf life. Keep cool and humid."
    },
    "Chili": {
        "shelf_life_days": 14,  "ideal_temp": 8,  "ideal_humidity": 90,
        "storage_tip":    "Refrigerate in perforated bags. Dry chili lasts 6+ months.",
        "spoilage_notes": "Fresh chili moderately perishable. Dry form very stable."
    },
    "Cucumber": {
        "shelf_life_days": 10,  "ideal_temp": 10, "ideal_humidity": 90,
        "storage_tip":    "Store at 10-12°C. Chilling injury below 10°C.",
        "spoilage_notes": "Moderate perishability. Keep away from ethylene-producing fruits."
    },
    "Pumpkin": {
        "shelf_life_days": 60,  "ideal_temp": 12, "ideal_humidity": 70,
        "storage_tip":    "Store in cool, dry, well-ventilated area. Cured skin lasts months.",
        "spoilage_notes": "Good shelf life when skin is intact and cured."
    },
    "Ash Gourd": {
        "shelf_life_days": 60,  "ideal_temp": 15, "ideal_humidity": 70,
        "storage_tip":    "Store whole in cool dry place. Waxy skin protects well.",
        "spoilage_notes": "Excellent shelf life when stored whole."
    },
    "Drumstick": {
        "shelf_life_days": 5,   "ideal_temp": 10, "ideal_humidity": 85,
        "storage_tip":    "Store in cool place. Bundle and keep moist.",
        "spoilage_notes": "Perishable. Sell within 3-5 days."
    },
    "Cluster Beans": {
        "shelf_life_days": 5,   "ideal_temp": 5,  "ideal_humidity": 90,
        "storage_tip":    "Refrigerate in perforated bags. Keep moist.",
        "spoilage_notes": "Perishable. Sell within 5 days."
    },
    "French Beans": {
        "shelf_life_days": 7,   "ideal_temp": 5,  "ideal_humidity": 90,
        "storage_tip":    "Store at 5-7°C in high humidity.",
        "spoilage_notes": "Moderately perishable."
    },
    "Peas": {
        "shelf_life_days": 7,   "ideal_temp": 0,  "ideal_humidity": 95,
        "storage_tip":    "Keep cool and moist. Sugar converts to starch quickly at warm temps.",
        "spoilage_notes": "Perishable fresh. Dried peas last 12+ months."
    },
    "Cabbage": {
        "shelf_life_days": 30,  "ideal_temp": 0,  "ideal_humidity": 95,
        "storage_tip":    "Store at near 0°C with high humidity. Remove outer leaves.",
        "spoilage_notes": "Good shelf life when cool. Avoid ethylene exposure."
    },
    "Cauliflower": {
        "shelf_life_days": 14,  "ideal_temp": 0,  "ideal_humidity": 95,
        "storage_tip":    "Store at near 0°C. Keep curd covered with leaves.",
        "spoilage_notes": "Moderate shelf life. Yellows quickly at warm temperatures."
    },
    "Broccoli": {
        "shelf_life_days": 7,   "ideal_temp": 0,  "ideal_humidity": 95,
        "storage_tip":    "Keep very cold and moist. Yellows rapidly.",
        "spoilage_notes": "Perishable. Sell within 5-7 days."
    },
    "Carrot": {
        "shelf_life_days": 30,  "ideal_temp": 0,  "ideal_humidity": 95,
        "storage_tip":    "Remove tops, store in cool humid conditions.",
        "spoilage_notes": "Good shelf life. Keep tops removed to prevent moisture loss."
    },
    "Radish": {
        "shelf_life_days": 14,  "ideal_temp": 0,  "ideal_humidity": 95,
        "storage_tip":    "Remove tops. Store in cool, moist conditions.",
        "spoilage_notes": "Moderate shelf life. Goes pithy if stored too long."
    },
    "Beetroot": {
        "shelf_life_days": 30,  "ideal_temp": 0,  "ideal_humidity": 95,
        "storage_tip":    "Remove tops, store in cool humid conditions.",
        "spoilage_notes": "Good shelf life when tops removed."
    },
    "Turnip": {
        "shelf_life_days": 30,  "ideal_temp": 0,  "ideal_humidity": 95,
        "storage_tip":    "Remove tops, store cool and moist.",
        "spoilage_notes": "Good shelf life when stored properly."
    },
    "Potato": {
        "shelf_life_days": 90,  "ideal_temp": 8,  "ideal_humidity": 90,
        "storage_tip":    "Store in dark, cool, humid area. Light causes greening (toxic).",
        "spoilage_notes": "Very good shelf life. Avoid light and excess moisture."
    },
    "Sweet Potato": {
        "shelf_life_days": 60,  "ideal_temp": 13, "ideal_humidity": 85,
        "storage_tip":    "Cure at 30°C for 1 week before storage. Store at 13-15°C.",
        "spoilage_notes": "Good shelf life when cured. Chilling sensitive."
    },
    "Onion": {
        "shelf_life_days": 90,  "ideal_temp": 0,  "ideal_humidity": 65,
        "storage_tip":    "Store in DRY, cool, well-ventilated area. Low humidity essential.",
        "spoilage_notes": "Excellent shelf life when dry. Moisture causes rotting."
    },
    "Garlic": {
        "shelf_life_days": 180, "ideal_temp": 0,  "ideal_humidity": 65,
        "storage_tip":    "Store in dry, cool, ventilated area. Braid for airflow.",
        "spoilage_notes": "Very good shelf life when dry and ventilated."
    },
    "Ginger": {
        "shelf_life_days": 30,  "ideal_temp": 13, "ideal_humidity": 90,
        "storage_tip":    "Store at 13°C with high humidity. Dry ginger lasts 6+ months.",
        "spoilage_notes": "Fresh ginger moderately perishable. Dry very stable."
    },
    "Turmeric": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 65,
        "storage_tip":    "Boil, dry and store in cool dry place. Powder lasts 1+ year.",
        "spoilage_notes": "Excellent shelf life when dried properly."
    },

    # ── Fruits ──
    "Banana": {
        "shelf_life_days": 5,   "ideal_temp": 13, "ideal_humidity": 85,
        "storage_tip":    "Keep at room temperature. Never refrigerate unripe.",
        "spoilage_notes": "Perishable. Sell within 3-5 days of ripening."
    },
    "Mango": {
        "shelf_life_days": 7,   "ideal_temp": 13, "ideal_humidity": 85,
        "storage_tip":    "Store at 13°C. Handle gently — bruising accelerates spoilage.",
        "spoilage_notes": "Perishable. Handle with care. Sell within 5-7 days."
    },
    "Papaya": {
        "shelf_life_days": 5,   "ideal_temp": 10, "ideal_humidity": 85,
        "storage_tip":    "Store ripe papaya at 10°C. Use within 5 days.",
        "spoilage_notes": "Perishable. Sell quickly once ripe."
    },
    "Guava": {
        "shelf_life_days": 5,   "ideal_temp": 8,  "ideal_humidity": 85,
        "storage_tip":    "Store at 8-10°C. Ripens quickly at room temperature.",
        "spoilage_notes": "Perishable. Sell within 3-5 days of ripening."
    },
    "Watermelon": {
        "shelf_life_days": 14,  "ideal_temp": 10, "ideal_humidity": 85,
        "storage_tip":    "Store whole at room temperature. Refrigerate after cutting.",
        "spoilage_notes": "Good shelf life whole. Sell cut melon same day."
    },
    "Muskmelon": {
        "shelf_life_days": 7,   "ideal_temp": 5,  "ideal_humidity": 85,
        "storage_tip":    "Store at 5-7°C when ripe. Keep away from other produce.",
        "spoilage_notes": "Moderate perishability. Strong ethylene producer."
    },
    "Grapes": {
        "shelf_life_days": 14,  "ideal_temp": 0,  "ideal_humidity": 90,
        "storage_tip":    "Refrigerate immediately. Keep dry — moisture causes mold.",
        "spoilage_notes": "Moderately perishable. Keep cool and dry."
    },
    "Pomegranate": {
        "shelf_life_days": 60,  "ideal_temp": 5,  "ideal_humidity": 80,
        "storage_tip":    "Store at 5°C. Thick skin protects well.",
        "spoilage_notes": "Excellent shelf life among fruits."
    },
    "Orange": {
        "shelf_life_days": 21,  "ideal_temp": 5,  "ideal_humidity": 85,
        "storage_tip":    "Refrigerate for longer shelf life. Do not wash until use.",
        "spoilage_notes": "Good shelf life. Avoid moisture on skin."
    },
    "Lemon": {
        "shelf_life_days": 30,  "ideal_temp": 10, "ideal_humidity": 85,
        "storage_tip":    "Store at 10-14°C. Lasts longer than most citrus.",
        "spoilage_notes": "Good shelf life. Keep cool and dry."
    },
    "Lime": {
        "shelf_life_days": 21,  "ideal_temp": 10, "ideal_humidity": 85,
        "storage_tip":    "Store at 10°C. Avoid bruising and moisture.",
        "spoilage_notes": "Good shelf life when stored cool."
    },
    "Coconut": {
        "shelf_life_days": 60,  "ideal_temp": 0,  "ideal_humidity": 80,
        "storage_tip":    "Store in cool dry place. Husk protects from damage.",
        "spoilage_notes": "Very good shelf life. Husk intact = longer life."
    },
    "Pineapple": {
        "shelf_life_days": 7,   "ideal_temp": 10, "ideal_humidity": 85,
        "storage_tip":    "Store at 10-13°C. Do not refrigerate below 10°C.",
        "spoilage_notes": "Perishable. Chilling sensitive. Sell within 1 week."
    },
    "Sapota": {
        "shelf_life_days": 5,   "ideal_temp": 15, "ideal_humidity": 85,
        "storage_tip":    "Store at 15°C. Ripens quickly at room temperature.",
        "spoilage_notes": "Very perishable once ripe. Sell within 3-5 days."
    },
    "Custard Apple": {
        "shelf_life_days": 3,   "ideal_temp": 15, "ideal_humidity": 85,
        "storage_tip":    "Handle very gently. Ripens and deteriorates very fast.",
        "spoilage_notes": "Extremely perishable. Sell within 1-3 days."
    },
    "Jackfruit": {
        "shelf_life_days": 7,   "ideal_temp": 13, "ideal_humidity": 85,
        "storage_tip":    "Store whole at 13°C. Cut jackfruit must be refrigerated.",
        "spoilage_notes": "Moderately perishable. Sell within 1 week."
    },
    "Strawberries": {
        "shelf_life_days": 3,   "ideal_temp": 0,  "ideal_humidity": 90,
        "storage_tip":    "Refrigerate immediately. Do not wash until ready to use.",
        "spoilage_notes": "Extremely perishable. Sell within 1-2 days."
    },
    "Amla": {
        "shelf_life_days": 14,  "ideal_temp": 5,  "ideal_humidity": 85,
        "storage_tip":    "Store at 5°C. High vitamin C content slows spoilage.",
        "spoilage_notes": "Moderate shelf life. Keep cool."
    },
    "Tamarind": {
        "shelf_life_days": 180, "ideal_temp": 20, "ideal_humidity": 50,
        "storage_tip":    "Store in cool, dry place. Shell protects pulp.",
        "spoilage_notes": "Excellent shelf life. Very stable when dry."
    },

    # ── Grains & Cereals ──
    "Rice": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Store in airtight containers. Moisture below 14% essential.",
        "spoilage_notes": "Excellent shelf life when dry. Moisture = mold risk."
    },
    "Wheat": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Store in clean, dry, ventilated warehouse. Monitor for insects.",
        "spoilage_notes": "Excellent shelf life. Keep moisture below 12-14%."
    },
    "Corn": {
        "shelf_life_days": 3,   "ideal_temp": 0,  "ideal_humidity": 95,
        "storage_tip":    "Fresh corn: refrigerate immediately. Dried corn: airtight dry storage.",
        "spoilage_notes": "Fresh very perishable. Dried corn lasts 1+ year."
    },
    "Maize": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Dry to 12% moisture before storage. Use airtight storage.",
        "spoilage_notes": "Excellent shelf life when properly dried."
    },
    "Sorghum": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Store dry in airtight bags. Monitor for weevils.",
        "spoilage_notes": "Excellent shelf life when dry."
    },
    "Bajra": {
        "shelf_life_days": 180, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Store in airtight containers. More prone to rancidity than wheat.",
        "spoilage_notes": "Good shelf life. High fat content — monitor for rancidity."
    },
    "Barley": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Store in cool, dry, ventilated warehouse.",
        "spoilage_notes": "Excellent shelf life when dry."
    },

    # ── Pulses & Legumes ──
    "Chickpea": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Store in airtight bags in cool dry place. Monitor for weevils.",
        "spoilage_notes": "Excellent shelf life when dry."
    },
    "Lentil": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Store in airtight containers. Keep cool and dry.",
        "spoilage_notes": "Excellent shelf life when dry."
    },
    "Pigeon Pea": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Store in airtight bags. Monitor for bruchid beetles.",
        "spoilage_notes": "Good shelf life. Monitor for insect damage."
    },
    "Black Gram": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Store dry in airtight containers.",
        "spoilage_notes": "Excellent shelf life when dry."
    },
    "Green Gram": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Store in airtight containers in cool dry place.",
        "spoilage_notes": "Excellent shelf life when dry."
    },
    "Soybean": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Dry to 11% moisture. Store in airtight cool storage.",
        "spoilage_notes": "Good shelf life. High oil content — monitor rancidity."
    },

    # ── Oilseeds & Cash Crops ──
    "Cotton": {
        "shelf_life_days": 365, "ideal_temp": 20, "ideal_humidity": 50,
        "storage_tip":    "Store in dry bales. Protect from moisture and fire.",
        "spoilage_notes": "Very stable when dry. Moisture causes quality loss."
    },
    "Sunflowers": {
        "shelf_life_days": 180, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Dry seeds to 9-10% moisture. Store in airtight cool storage.",
        "spoilage_notes": "Good shelf life. High oil = rancidity risk if warm."
    },
    "Groundnut": {
        "shelf_life_days": 180, "ideal_temp": 10, "ideal_humidity": 65,
        "storage_tip":    "Cure and dry thoroughly. Aflatoxin risk in humid storage.",
        "spoilage_notes": "Aflatoxin risk if stored damp. Keep very dry."
    },
    "Sesame": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Store in airtight container. Very prone to rancidity.",
        "spoilage_notes": "Good shelf life but monitor for rancidity."
    },
    "Mustard": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Store in airtight cool dry place.",
        "spoilage_notes": "Excellent shelf life when dry."
    },
    "Jute": {
        "shelf_life_days": 180, "ideal_temp": 20, "ideal_humidity": 50,
        "storage_tip":    "Store in dry warehouse. Avoid moisture.",
        "spoilage_notes": "Good shelf life when kept dry."
    },
    "Sugarcane": {
        "shelf_life_days": 2,   "ideal_temp": 5,  "ideal_humidity": 85,
        "storage_tip":    "Process or sell within 24-48 hours of cutting.",
        "spoilage_notes": "Extremely perishable. Must sell same day of cutting."
    },

    # ── Spices & Plantation Crops ──
    "Coffee": {
        "shelf_life_days": 180, "ideal_temp": 20, "ideal_humidity": 50,
        "storage_tip":    "Store green beans in airtight container away from light.",
        "spoilage_notes": "Good shelf life as green beans."
    },
    "Cinnamon": {
        "shelf_life_days": 730, "ideal_temp": 20, "ideal_humidity": 40,
        "storage_tip":    "Store in airtight container away from light and heat.",
        "spoilage_notes": "Very long shelf life as dried spice."
    },
    "Pepper": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 65,
        "storage_tip":    "Store whole peppercorns in airtight container.",
        "spoilage_notes": "Excellent shelf life when dried properly."
    },
    "Cardamom": {
        "shelf_life_days": 365, "ideal_temp": 10, "ideal_humidity": 60,
        "storage_tip":    "Store in airtight container in cool dark place.",
        "spoilage_notes": "Good shelf life when stored airtight."
    },
    "Cumin": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Store in airtight container away from light.",
        "spoilage_notes": "Excellent shelf life when dry."
    },
    "Coriander Seeds": {
        "shelf_life_days": 365, "ideal_temp": 15, "ideal_humidity": 40,
        "storage_tip":    "Store in airtight container. Whole seeds last longer than ground.",
        "spoilage_notes": "Excellent shelf life as whole seeds."
    },

    # ── Default Fallback ──
    "Default": {
        "shelf_life_days": 7,   "ideal_temp": 15, "ideal_humidity": 65,
        "storage_tip":    "Store in cool, dry, ventilated area. Avoid direct sunlight.",
        "spoilage_notes": "Follow standard post-harvest handling practices."
    }
}



# CROP TO DATASET MAP
# Maps mandi crops → nearest ML model crop
# ML model knows only 10 crops from dataset:
# Carrots, Chili, Cinnamon, Corn, Eggplant,
# Rice, Strawberries, Sunflowers, Tomato, Wheat
#
# Logic: map by soil/climate similarity

CROP_TO_DATASET_MAP = {
    # Vegetables
    "Onion":          "Carrots",      # root vegetable, similar soil
    "Potato":         "Carrots",      # root vegetable, similar soil
    "Sweet Potato":   "Carrots",      # root vegetable
    "Carrot":         "Carrots",      # exact match
    "Radish":         "Carrots",      # root vegetable
    "Beetroot":       "Carrots",      # root vegetable
    "Turnip":         "Carrots",      # root vegetable
    "Garlic":         "Carrots",      # bulb vegetable, similar soil
    "Ginger":         "Corn",         # tropical, high moisture
    "Spinach":        "Eggplant",     # leafy vegetable
    "Coriander":      "Eggplant",     # leafy herb
    "Fenugreek":      "Eggplant",     # leafy vegetable
    "Cabbage":        "Eggplant",     # leafy vegetable
    "Cauliflower":    "Eggplant",     # brassica vegetable
    "Broccoli":       "Eggplant",     # brassica vegetable
    "Okra":           "Eggplant",     # tropical vegetable
    "Capsicum":       "Chili",        # same family (Capsicum)
    "Bitter Gourd":   "Eggplant",     # tropical vegetable
    "Bottle Gourd":   "Eggplant",     # tropical vegetable
    "Ridge Gourd":    "Eggplant",     # tropical vegetable
    "Snake Gourd":    "Eggplant",     # tropical vegetable
    "Pumpkin":        "Corn",         # warm climate, high moisture
    "Ash Gourd":      "Corn",         # tropical gourd
    "Cucumber":       "Eggplant",     # tropical vegetable
    "Drumstick":      "Sunflowers",   # dryland tropical
    "Cluster Beans":  "Corn",         # legume vegetable
    "French Beans":   "Corn",         # legume vegetable
    "Peas":           "Corn",         # legume vegetable
    "Turmeric":       "Corn",         # tropical rhizome

    # Fruits
    "Banana":         "Corn",         # tropical, high moisture
    "Mango":          "Sunflowers",   # warm climate tree
    "Papaya":         "Corn",         # tropical fruit
    "Guava":          "Sunflowers",   # tropical tree fruit
    "Watermelon":     "Corn",         # warm climate, high moisture
    "Muskmelon":      "Corn",         # warm climate
    "Grapes":         "Strawberries", # fruit crop, similar soil
    "Pomegranate":    "Sunflowers",   # dryland fruit
    "Orange":         "Sunflowers",   # citrus tree
    "Lemon":          "Sunflowers",   # citrus tree
    "Lime":           "Sunflowers",   # citrus tree
    "Coconut":        "Corn",         # tropical, coastal
    "Pineapple":      "Corn",         # tropical fruit
    "Sapota":         "Sunflowers",   # dryland tropical fruit
    "Custard Apple":  "Corn",         # tropical fruit
    "Jackfruit":      "Corn",         # tropical tree fruit
    "Amla":           "Sunflowers",   # dryland fruit
    "Tamarind":       "Sunflowers",   # dryland tree

    # Grains
    "Sorghum":        "Wheat",        # dryland cereal
    "Bajra":          "Wheat",        # dryland cereal
    "Barley":         "Wheat",        # cereal crop
    "Maize":          "Corn",         # exact match

    # Pulses
    "Lentil":         "Wheat",        # rabi pulse, similar conditions
    "Chickpea":       "Wheat",        # rabi pulse
    "Pigeon Pea":     "Corn",         # kharif pulse
    "Black Gram":     "Corn",         # kharif pulse
    "Green Gram":     "Corn",         # kharif pulse
    "Soybean":        "Corn",         # kharif legume

    # Oilseeds & Cash Crops
    "Groundnut":      "Sunflowers",   # oilseed, similar conditions
    "Sesame":         "Sunflowers",   # oilseed
    "Mustard":        "Wheat",        # rabi oilseed
    "Cotton":         "Sunflowers",   # dryland cash crop
    "Jute":           "Corn",         # tropical fiber crop
    "Sugarcane":      "Corn",         # tropical, high moisture

    # Spices
    "Pepper":         "Corn",         # tropical spice
    "Cardamom":       "Corn",         # tropical spice
    "Cumin":          "Wheat",        # dryland spice
    "Coriander Seeds":"Wheat",        # dryland spice
    "Coffee":         "Corn",         # tropical plantation

    # Direct matches (already in dataset)
    "Carrots":        "Carrots",
    "Chili":          "Chili",
    "Cinnamon":       "Cinnamon",
    "Corn":           "Corn",
    "Eggplant":       "Eggplant",
    "Rice":           "Rice",
    "Strawberries":   "Strawberries",
    "Sunflowers":     "Sunflowers",
    "Tomato":         "Tomato",
    "Wheat":          "Wheat",
}



# HELPER — GET PROFILE
# Returns profile for a crop,
# falls back to Default if not found

def get_crop_profile(crop: str) -> dict:
    """Returns crop profile, falling back to Default if crop not found."""
    return CROP_PROFILES.get(crop.strip().title(), CROP_PROFILES["Default"])


def get_model_crop(crop: str) -> str:
    """Maps any crop to its nearest ML model equivalent."""
    return CROP_TO_DATASET_MAP.get(crop.strip().title(), "Tomato")



# QUICK TEST — python crop_profiles.py

if __name__ == "__main__":
    print(f"Total crops in CROP_PROFILES : {len(CROP_PROFILES)}")
    print(f"Total crops in DATASET_MAP   : {len(CROP_TO_DATASET_MAP)}")

    test_crops = ["Onion", "Banana", "Groundnut", "Sugarcane",
                  "Pepper", "Bajra", "UnknownCrop"]

    print("\n── Sample Lookups ──")
    for crop in test_crops:
        profile    = get_crop_profile(crop)
        model_crop = get_model_crop(crop)
        print(f"  {crop:<15} → shelf:{profile['shelf_life_days']:>4}d "
              f"| model_crop: {model_crop}")