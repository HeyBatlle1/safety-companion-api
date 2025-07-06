#!/usr/bin/env python3
"""
Safety Companion Integration for Gemini - Fixed Schema
"""

import google.generativeai as genai
import requests
import json

# Configure Gemini with your API key
genai.configure(api_key="AIzaSyBFHI86UKgiTq7bObi_6hKOjOjwnULIRp8")

def get_construction_risk_profile(naics_code: str):
    """Get comprehensive safety risk profile for a construction industry NAICS code"""
    response = requests.get(f"http://localhost:8000/risk-profile/{naics_code}")
    return response.json()

def get_industry_safety_benchmark(naics_prefix: str):
    """Get safety benchmarks for construction industry group"""
    response = requests.get(f"http://localhost:8000/industry-benchmark/{naics_prefix}")
    return response.json()

def find_similar_risk_industries(injury_rate: float, tolerance: float = 0.5):
    """Find construction industries with similar safety risk profiles"""
    response = requests.get(f"http://localhost:8000/similar-industries/{injury_rate}?tolerance={tolerance}")
    return response.json()

# Initialize Gemini model with function calling
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    tools=[get_construction_risk_profile, get_industry_safety_benchmark, find_similar_risk_industries]
)

def chat_with_safety_intelligence(user_message):
    """Chat with Gemini using Safety Companion intelligence"""
    
    try:
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# Test the integration
if __name__ == "__main__":
    print("=== Safety Companion + Gemini Integration ===")
    print("Make sure your Safety API is running on localhost:8000")
    print()
    
    # Test basic functionality first
    try:
        # Test our Safety API directly
        test_response = requests.get("http://localhost:8000/")
        print("✅ Safety API is responding")
        
        # Test Gemini integration
        test_query = "What's the safety risk profile for construction of buildings? Use NAICS code 236."
        
        print(f"Testing query: {test_query}")
        response = chat_with_safety_intelligence(test_query)
        print(f"Gemini response: {response}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Safety API not running. Start it with: python3 safety_api_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Interactive mode
    while True:
        user_input = input("\nAsk about construction safety (or 'quit'): ")
        if user_input.lower() == 'quit':
            break
            
        try:
            response = chat_with_safety_intelligence(user_input)
            print(f"\nGemini: {response}")
        except Exception as e:
            print(f"Error: {e}")
