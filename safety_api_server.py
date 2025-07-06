#!/usr/bin/env python3
"""
Safety Companion API Server
Enterprise construction safety intelligence via FastAPI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://fbjjqwfcmzrpmytieajp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZiampxd2ZjbXpycG15dGllYWpwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNTQ5MTg5NCwiZXhwIjoyMDUxMDY3ODk0fQ.o8tm3DIAvLSN4Hcuh33nw54yyNChBLmMqpSPX6vsMis"

app = FastAPI(
    title="Safety Companion API",
    description="Enterprise construction safety intelligence and risk assessment API",
    version="1.0.0"
)

# CORS configuration for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API responses
class RiskProfile(BaseModel):
    naics_code: str
    industry_name: str
    injury_rate: Optional[float]
    fatalities_2023: Optional[int]
    risk_score: float
    risk_category: str
    recommendations: List[str]

class IndustryBenchmark(BaseModel):
    naics_code: str
    industry_name: str
    injury_rate: Optional[float]

class SafetyIntelligenceAPI:
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def get_risk_profile(self, naics_code: str) -> Dict[str, Any]:
        """Get comprehensive risk profile for NAICS code"""
        
        # Get injury rate data
        injury_result = self.supabase.table('osha_injury_rates').select('*').eq('naics_code', naics_code).eq('data_source', 'BLS_Table_1_2023').execute()
        
        # Get fatality data
        fatality_result = self.supabase.table('osha_injury_rates').select('*').eq('naics_code', naics_code).eq('data_source', 'BLS_FATALITIES_A1_2023').execute()
        
        injury_data = injury_result.data[0] if injury_result.data else None
        fatality_data = fatality_result.data[0] if fatality_result.data else None
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(injury_data, fatality_data)
        
        return {
            'naics_code': naics_code,
            'industry_name': injury_data['industry_name'] if injury_data else 'Unknown Industry',
            'injury_rate': injury_data['injury_rate'] if injury_data else None,
            'fatalities_2023': fatality_data['total_cases'] if fatality_data else None,
            'risk_score': risk_score,
            'risk_category': self._get_risk_category(risk_score),
            'recommendations': self._get_safety_recommendations(risk_score)
        }
    
    def get_industry_benchmark(self, naics_prefix: str) -> List[Dict[str, Any]]:
        """Get benchmark data for industry group"""
        injury_result = self.supabase.table('osha_injury_rates').select('*').like('naics_code', f'{naics_prefix}%').eq('data_source', 'BLS_Table_1_2023').execute()
        
        return [{
            'naics_code': row['naics_code'],
            'industry_name': row['industry_name'],
            'injury_rate': row['injury_rate']
        } for row in injury_result.data]
    
    def search_similar_industries(self, injury_rate_target: float, tolerance: float = 0.5) -> List[Dict[str, Any]]:
        """Find industries with similar injury rates"""
        all_data = self.supabase.table('osha_injury_rates').select('*').eq('data_source', 'BLS_Table_1_2023').execute()
        
        similar = []
        for row in all_data.data:
            if row['injury_rate'] and abs(row['injury_rate'] - injury_rate_target) <= tolerance:
                similar.append({
                    'naics_code': row['naics_code'],
                    'industry_name': row['industry_name'],
                    'injury_rate': row['injury_rate'],
                    'rate_difference': abs(row['injury_rate'] - injury_rate_target)
                })
        
        return sorted(similar, key=lambda x: x['rate_difference'])
    
    def _calculate_risk_score(self, injury_data, fatality_data) -> float:
        """Enterprise risk scoring algorithm"""
        score = 0.0
        
        if injury_data and injury_data['injury_rate']:
            score += min(injury_data['injury_rate'] * 10, 50)
        
        if fatality_data and fatality_data['total_cases']:
            score += min(fatality_data['total_cases'] * 0.5, 50)
        
        return round(min(score, 100), 1)
    
    def _get_risk_category(self, risk_score: float) -> str:
        """Categorize risk level"""
        if risk_score >= 75: return "CRITICAL"
        elif risk_score >= 50: return "HIGH"
        elif risk_score >= 25: return "MODERATE"
        else: return "LOW"
    
    def _get_safety_recommendations(self, risk_score: float) -> List[str]:
        """Generate safety recommendations"""
        if risk_score >= 75:
            return [
                "Implement immediate safety intervention program",
                "Mandatory daily safety briefings",
                "Enhanced PPE requirements",
                "Third-party safety audit recommended"
            ]
        elif risk_score >= 50:
            return [
                "Increase safety training frequency",
                "Review and update safety protocols",
                "Implement weekly safety inspections"
            ]
        elif risk_score >= 25:
            return [
                "Maintain current safety standards",
                "Regular safety training updates",
                "Monitor injury trends"
            ]
        else:
            return [
                "Continue best practices",
                "Share safety insights with industry peers"
            ]

# Initialize safety API
safety_api = SafetyIntelligenceAPI()

# API Endpoints
@app.get("/", summary="API Health Check")
async def root():
    return {
        "service": "Safety Companion API",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": [
            "/risk-profile/{naics_code}",
            "/industry-benchmark/{naics_prefix}",
            "/similar-industries/{injury_rate}"
        ]
    }

@app.get("/risk-profile/{naics_code}", response_model=RiskProfile, summary="Get Risk Profile")
async def get_risk_profile(naics_code: str):
    """
    Get comprehensive safety risk profile for a NAICS industry code
    
    - **naics_code**: NAICS industry code (e.g., '236', '2361')
    """
    try:
        profile = safety_api.get_risk_profile(naics_code)
        return RiskProfile(**profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving risk profile: {str(e)}")

@app.get("/industry-benchmark/{naics_prefix}", response_model=List[IndustryBenchmark], summary="Get Industry Benchmarks")
async def get_industry_benchmark(naics_prefix: str):
    """
    Get safety benchmarks for an industry group
    
    - **naics_prefix**: NAICS prefix for industry group (e.g., '23' for construction)
    """
    try:
        benchmarks = safety_api.get_industry_benchmark(naics_prefix)
        return [IndustryBenchmark(**benchmark) for benchmark in benchmarks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving benchmarks: {str(e)}")

@app.get("/similar-industries/{injury_rate}", summary="Find Similar Industries")
async def get_similar_industries(injury_rate: float, tolerance: float = 0.5):
    """
    Find industries with similar injury rates for comparative analysis
    
    - **injury_rate**: Target injury rate to match
    - **tolerance**: Acceptable difference in injury rate (default: 0.5)
    """
    try:
        similar = safety_api.search_similar_industries(injury_rate, tolerance)
        return similar
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar industries: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
