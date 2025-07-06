#!/usr/bin/env python3
"""
Safety Companion Integration for Gemini
Uses Gemini's function calling to access our Safety API
"""

import google.generativeai as genai
import requests
import json

# Configure Gemini
genai.configure(api_key="your-gemini-api-key")

# Define safety functions for Gemini
safety_functions = [
    {
        "name": "get_construction_risk_profile", 
        "description": "Get comprehensive safety risk profile for a construction industry NAICS code",
        "parameters": {
            "type": "object",
            "properties": {
                "naics_code": {
                    "type": "string",
                    "description": "NAICS industry code (e.g., '236', '23815')"
                }
            },
            "required": ["naics_code"]
        }
    },
    {
        "name": "get_industry_safety_benchmark",
        "description": "Get safety benchmarks for construction industry group",
        "parameters": {
            "type": "object", 
            "properties": {
                "naics_prefix": {
                    "type": "string",
                    "description": "NAICS prefix for industry group (e.g., '23' for construction)"
                }
            },
            "required": ["naics_prefix"]
        }
    },
    {
        "name": "find_similar_risk_industries",
        "description": "Find construction industries with similar safety risk profiles",
        "parameters": {
            "type": "object",
            "properties": {
                "injury_rate": {
                    "type": "number",
                    "description": "Target injury rate to match"
                },
                "tolerance": {
                    "type": "number", 
                    "description": "Acceptable difference in injury rate",
                    "default": 0.5
                }
            },
            "required": ["injury_rate"]
        }
    }
]

def call_safety_api(function_name, **kwargs):
    """Call our Safety Companion API"""
    base_url = "http://localhost:8000"
    
    if function_name == "get_construction_risk_profile":
        response = requests.get(f"{base_url}/risk-profile/{kwargs['naics_code']}")
    elif function_name == "get_industry_safety_benchmark":
        response = requests.get(f"{base_url}/industry-benchmark/{kwargs['naics_prefix']}")
    elif function_name == "find_similar_risk_industries":
        tolerance = kwargs.get('tolerance', 0.5)
        response = requests.get(f"{base_url}/similar-industries/{kwargs['injury_rate']}?tolerance={tolerance}")
    
    return response.json()

# Initialize Gemini model with function calling
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    tools=safety_functions
)

def chat_with_safety_intelligence(user_message):
    """Chat with Gemini using Safety Companion intelligence"""
    
    chat = model.start_chat()
    response = chat.send_message(user_message)
    
    # Handle function calls
    if response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        function_name = function_call.name
        function_args = dict(function_call.args)
        
        # Call our Safety API
        api_result = call_safety_api(function_name, **function_args)
        
        # Send result back to Gemini
        response = chat.send_message([
            genai.types.FunctionResponse(
                name=function_name,
                response=api_result
            )
        ])
    
    return response.text

# Example usage
if __name__ == "__main__":
    print("Safety Companion + Gemini Integration")
    
    while True:
        user_input = input("\nAsk about construction safety: ")
        if user_input.lower() == 'quit':
            break
            
        try:
            response = chat_with_safety_intelligence(user_input)
            print(f"\nGemini: {response}")
        except Exception as e:
            print(f"Error: {e}")
