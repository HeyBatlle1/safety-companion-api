#!/usr/bin/env python3
"""
Weather-Safety Intelligence Integration
Combines Open-Meteo weather data with OSHA safety analysis via Gemini 2.0 Flash
"""

import httpx
import google.generativeai as genai
from typing import Dict, Any
import json
from datetime import datetime

# Configure Gemini 2.0 Flash
genai.configure(api_key="AIzaSyBFHI86UKgiTq7bObi_6hKOjOjwnULIRp8")
model = genai.GenerativeModel('gemini-2.0-flash-exp')

class WeatherSafetyService:
    def __init__(self):
        self.weather_api_base = "https://api.open-meteo.com/v1"
        self.lawrence_coords = {"lat": 39.8528, "lon": -86.0253}  # Lawrence, IN
    
    async def get_current_weather(self) -> Dict[str, Any]:
        """Get current weather conditions for Lawrence, IN"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.weather_api_base}/forecast",
                params={
                    "latitude": self.lawrence_coords["lat"],
                    "longitude": self.lawrence_coords["lon"],
                    "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m",
                    "temperature_unit": "fahrenheit",
                    "wind_speed_unit": "mph",
                    "precipitation_unit": "inch"
                }
            )
            return response.json()
    
    async def get_weather_forecast(self, days: int = 3) -> Dict[str, Any]:
        """Get weather forecast for next few days"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.weather_api_base}/forecast",
                params={
                    "latitude": self.lawrence_coords["lat"],
                    "longitude": self.lawrence_coords["lon"],
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,wind_direction_10m_dominant",
                    "forecast_days": days,
                    "temperature_unit": "fahrenheit",
                    "wind_speed_unit": "mph",
                    "precipitation_unit": "inch"
                }
            )
            return response.json()
    
    async def analyze_weather_safety_risk(self, naics_code: str, safety_profile: Dict[str, Any]) -> str:
        """Use Gemini 2.0 Flash to analyze weather + safety risk"""
        
        # Get current weather
        weather_data = await self.get_current_weather()
        forecast_data = await self.get_weather_forecast()
        
        # Extract key weather conditions
        current = weather_data.get("current", {})
        temp_f = current.get("temperature_2m", "N/A")
        humidity = current.get("relative_humidity_2m", "N/A")
        precipitation = current.get("precipitation", "N/A")
        wind_speed = current.get("wind_speed_10m", "N/A")
        wind_direction = current.get("wind_direction_10m", "N/A")
        
        prompt = f"""
        Analyze construction safety risk considering current weather conditions in Lawrence, Indiana:
        
        CURRENT WEATHER CONDITIONS:
        - Temperature: {temp_f}°F
        - Humidity: {humidity}%
        - Precipitation: {precipitation} inches
        - Wind Speed: {wind_speed} mph
        - Wind Direction: {wind_direction}°
        
        INDUSTRY SAFETY PROFILE:
        - Industry: {safety_profile.get('industry_name')}
        - NAICS Code: {naics_code}
        - Base Injury Rate: {safety_profile.get('injury_rate', 'N/A')} per 100 workers
        - Risk Score: {safety_profile.get('risk_score', 'N/A')}/100
        - Risk Category: {safety_profile.get('risk_category')}
        
        3-DAY FORECAST:
        {json.dumps(forecast_data.get('daily', {}), indent=2)}
        
        Provide specific weather-aware safety recommendations:
        
        1. IMMEDIATE WEATHER HAZARDS: How do current conditions affect construction safety?
        2. TRADE-SPECIFIC RISKS: Weather risks specific to this construction trade
        3. EQUIPMENT & PPE ADJUSTMENTS: What safety equipment changes are needed?
        4. WORK SCHEDULE RECOMMENDATIONS: Should work be modified or postponed?
        5. ENHANCED SAFETY PROTOCOLS: Additional safety measures for current weather
        6. 3-DAY OUTLOOK: Upcoming weather-related safety considerations
        
        Focus on actionable, specific guidance for construction supervisors and safety managers.
        """
        
        response = model.generate_content(prompt)
        return response.text

# Create service instance
weather_safety_service = WeatherSafetyService()
