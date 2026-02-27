"""
Quick test to verify OLA Maps transit endpoint works
"""

import os
from dotenv import load_dotenv
from py_olamaps.OlaMaps import OlaMaps

load_dotenv()

print("=" * 60)
print("Testing OLA Maps Transit Time Calculation")
print("=" * 60)

# Check if API key is loaded
api_key = os.getenv("OLA_MAPS_API_KEY")
print(f"\n1. OLA_MAPS_API_KEY loaded: {bool(api_key)}")
if api_key:
    print(f"   Key starts with: {api_key[:20]}...")

# Test OLA Maps directly
print("\n2. Testing OLA Maps API directly...")
try:
    client = OlaMaps(api_key=api_key)
    
    # Pune to Mumbai
    origin = "18.5204,73.8567"  # Pune
    dest = "19.0760,72.8777"    # Mumbai
    
    result = client.routing.directions(origin, dest)
    
    routes = result.get("routes", [])
    if routes:
        leg = routes[0]["legs"][0]
        duration_secs = leg.get("duration", 0)
        distance_meters = leg.get("distance", 0)
        
        transit_hours = round(duration_secs / 3600, 1)
        distance_km = round(distance_meters / 1000, 1)
        
        print(f"   ✓ Success!")
        print(f"   Transit Hours: {transit_hours}")
        print(f"   Distance: {distance_km} km")
    else:
        print(f"   ✗ No routes found")
        print(f"   Response: {result}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
