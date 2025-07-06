
#!/usr/bin/env python3
"""
Safety Companion + Gemini 2.0 Flash Integration
"""

import google.generativeai as genai
import requests
import json

# Configure Gemini 2.0 Flash - replace with your actual API key
genai.configure(api_key="AIzaSyBFHI86UKgiTq7bObi_6hKOjOjwnULIRp8")

# Use Gemini 2.0 Flash model
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def get_safety_data_and_analyze(query):
    """Get safety data and have Gemini 2.0 Flash analyze it"""
    
    # Extract NAICS code from query or use default
    naics_code = "236"  # Construction of buildings
    
    # Detect what the user is asking for
    if "glass" in query.lower() or "glazing" in query.lower():
        naics_code = "23815"
    elif "framing" in query.lower():
        naics_code = "23813"
    elif "roofing" in query.lower():
        naics_code = "23816"
    elif "electrical" in query.lower():
        naics_code = "23821"
    elif "siding" in query.lower():
        naics_code = "23817"
    elif "benchmark" in query.lower() or "compare" in query.lower():
        # Get benchmark data
        try:
            response = requests.get("http://localhost:8000/industry-benchmark/23")
            benchmark_data = response.json()
            
            prompt = f"""
            Analyze this construction industry safety benchmark data:
            
            {json.dumps(benchmark_data, indent=2)}
            
            User question: {query}
            
            Provide insights about:
            1. Highest risk construction trades (injury rates above 3.0)
            2. Safest construction trades (injury rates below 2.0)
            3. Industry patterns and specific recommendations
            4. Focus areas for safety improvement
            """
            
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error getting benchmark data: {e}"
    
    # Get risk profile for specific NAICS
    try:
        response = requests.get(f"http://localhost:8000/risk-profile/{naics_code}")
        safety_data = response.json()
        
        prompt = f"""
        Analyze this construction safety risk profile using real 2023 OSHA data:
        
        Industry: {safety_data.get('industry_name', 'Unknown')}
        NAICS Code: {safety_data.get('naics_code', 'Unknown')}
        Injury Rate: {safety_data.get('injury_rate', 'N/A')} per 100 workers
        Fatalities (2023): {safety_data.get('fatalities_2023', 'N/A')}
        Risk Score: {safety_data.get('risk_score', 'N/A')}/100
        Risk Category: {safety_data.get('risk_category', 'Unknown')}
        Current Recommendations: {safety_data.get('recommendations', [])}
        
        User question: {query}
        
        Provide specific, actionable analysis:
        1. What this risk level means for construction companies
        2. Trade-specific safety recommendations beyond the generic ones
        3. Comparison to construction industry averages
        4. Key focus areas for immediate safety improvement
        5. Regulatory compliance considerations
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error getting safety data: {e}"

if __name__ == "__main__":
    print("=== Safety Companion + Gemini 2.0 Flash Integration ===")
    
    # Test connection
    try:
        test_response = requests.get("http://localhost:8000/")
        print("✅ Safety API is responding")
    except:
        print("❌ Safety API not running")
        exit()
    
    print("\nExample queries:")
    print("- 'What's the safety risk for glass and glazing contractors?'")
    print("- 'Compare construction safety across all trades'")  
    print("- 'Analyze safety for siding contractors'")
    print("- 'Show me the most dangerous construction trades'")
    
    while True:
        user_input = input("\nAsk about construction safety (or 'quit'): ")
        if user_input.lower() == 'quit':
            break
            
        try:
            response = get_safety_data_and_analyze(user_input)
            print(f"\n🤖 Gemini 2.0 Flash Analysis:\n{response}")
        except Exception as e:
            print(f"Error: {e}")
