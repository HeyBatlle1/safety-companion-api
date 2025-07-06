#!/usr/bin/env python3
"""
JHSA (Job Hazard Safety Assessment) Extension for Safety Companion API
Based on OSHA 3071 methodology
"""

from typing import List, Dict, Any
import json

class JHSAGenerator:
    def __init__(self, safety_api):
        self.safety_api = safety_api
        
        # OSHA 3071 Common Construction Hazards Database
        self.construction_hazards = {
            'height_work': {
                'hazards': ['Falls from elevation', 'Falling objects', 'Ladder/scaffold failure'],
                'controls': ['Fall protection harness', 'Guardrails', 'Safety nets', 'Ladder inspection']
            },
            'heavy_lifting': {
                'hazards': ['Back injury', 'Crush injury', 'Strain/sprain'],
                'controls': ['Mechanical lifting aids', 'Team lifting', 'Proper lifting technique', 'Weight limits']
            },
            'power_tools': {
                'hazards': ['Cuts/lacerations', 'Eye injury', 'Noise exposure', 'Electrical shock'],
                'controls': ['Cut-resistant gloves', 'Safety glasses', 'Hearing protection', 'GFCI protection']
            },
            'glass_handling': {
                'hazards': ['Cuts from broken glass', 'Back strain', 'Eye injury from glass shards'],
                'controls': ['Cut-resistant gloves', 'Proper lifting technique', 'Safety glasses', 'Glass lifters']
            },
            'welding': {
                'hazards': ['Burns', 'Eye damage', 'Fume inhalation', 'Fire risk'],
                'controls': ['Welding helmet', 'Fire extinguisher', 'Ventilation', 'Fire watch']
            },
            'confined_space': {
                'hazards': ['Oxygen deficiency', 'Toxic atmosphere', 'Engulfment'],
                'controls': ['Atmospheric testing', 'Ventilation', 'Entry permit', 'Attendant']
            }
        }
        
        # Trade-specific task templates
        self.trade_templates = {
            '23815': {  # Glass and Glazing
                'common_tasks': [
                    'Material delivery and staging',
                    'Glass cutting and preparation', 
                    'Installation of anchors and frames',
                    'Glass panel lifting and positioning',
                    'Glazing compound application',
                    'Final inspection and cleanup'
                ],
                'primary_hazards': ['height_work', 'glass_handling', 'heavy_lifting']
            },
            '23813': {  # Framing
                'common_tasks': [
                    'Material layout and preparation',
                    'Frame assembly on ground',
                    'Frame lifting and positioning',
                    'Fastening and securing',
                    'Plumb and square checking',
                    'Temporary bracing installation'
                ],
                'primary_hazards': ['height_work', 'heavy_lifting', 'power_tools']
            },
            '23816': {  # Roofing
                'common_tasks': [
                    'Material hoisting to roof level',
                    'Roof surface preparation',
                    'Installation of underlayment',
                    'Shingle/tile installation',
                    'Flashing installation',
                    'Cleanup and debris removal'
                ],
                'primary_hazards': ['height_work', 'heavy_lifting', 'power_tools']
            }
        }
    
    def generate_jhsa_template(self, naics_code: str, job_title: str, custom_tasks: List[str] = None):
        """Generate JHSA template based on NAICS code and job requirements"""
        
        # Get industry risk profile from existing Safety API
        risk_profile = self.safety_api.get_risk_profile(naics_code)
        
        # Get trade-specific template
        trade_template = self.trade_templates.get(naics_code, {})
        
        # Use custom tasks or default trade tasks
        tasks = custom_tasks or trade_template.get('common_tasks', [
            'Task setup and preparation',
            'Main work activity',
            'Tool/equipment operation',
            'Material handling',
            'Quality inspection',
            'Cleanup and securing'
        ])
        
        jhsa_template = {
            'job_info': {
                'job_title': job_title,
                'naics_code': naics_code,
                'industry_name': risk_profile.get('industry_name', 'Unknown'),
                'date_created': None,  # To be filled by user
                'analyst_name': None,  # To be filled by user
                'job_location': None   # To be filled by user
            },
            'risk_context': {
                'industry_injury_rate': risk_profile.get('injury_rate'),
                'industry_risk_score': risk_profile.get('risk_score'),
                'industry_risk_category': risk_profile.get('risk_category'),
                'fatalities_2023': risk_profile.get('fatalities_2023')
            },
            'job_steps': []
        }
        
        # Generate hazard analysis for each task step
        for i, task in enumerate(tasks, 1):
            step = {
                'step_number': i,
                'task_description': task,
                'potential_hazards': self._identify_hazards_for_task(task, naics_code),
                'preventive_measures': self._get_preventive_measures_for_task(task, naics_code),
                'required_ppe': self._get_required_ppe_for_task(task, naics_code),
                'training_requirements': self._get_training_requirements(task, naics_code)
            }
            jhsa_template['job_steps'].append(step)
        
        return jhsa_template
    
    def _identify_hazards_for_task(self, task: str, naics_code: str):
        """Identify potential hazards for a specific task"""
        hazards = []
        task_lower = task.lower()
        
        # Height-related hazards
        if any(keyword in task_lower for keyword in ['lifting', 'positioning', 'installation', 'roof', 'elevation']):
            hazards.extend(self.construction_hazards['height_work']['hazards'])
        
        # Glass handling hazards
        if any(keyword in task_lower for keyword in ['glass', 'panel', 'glazing', 'cutting']):
            hazards.extend(self.construction_hazards['glass_handling']['hazards'])
        
        # Heavy lifting hazards
        if any(keyword in task_lower for keyword in ['material', 'lifting', 'moving', 'hoisting']):
            hazards.extend(self.construction_hazards['heavy_lifting']['hazards'])
        
        # Power tool hazards
        if any(keyword in task_lower for keyword in ['cutting', 'drilling', 'fastening', 'assembly']):
            hazards.extend(self.construction_hazards['power_tools']['hazards'])
        
        # Remove duplicates and return
        return list(set(hazards))
    
    def _get_preventive_measures_for_task(self, task: str, naics_code: str):
        """Get preventive measures for identified hazards"""
        measures = []
        task_lower = task.lower()
        
        if any(keyword in task_lower for keyword in ['lifting', 'positioning', 'installation']):
            measures.extend(self.construction_hazards['height_work']['controls'])
        
        if any(keyword in task_lower for keyword in ['glass', 'panel', 'glazing']):
            measures.extend(self.construction_hazards['glass_handling']['controls'])
        
        if any(keyword in task_lower for keyword in ['material', 'lifting', 'moving']):
            measures.extend(self.construction_hazards['heavy_lifting']['controls'])
        
        if any(keyword in task_lower for keyword in ['cutting', 'drilling', 'fastening']):
            measures.extend(self.construction_hazards['power_tools']['controls'])
        
        return list(set(measures))
    
    def _get_required_ppe_for_task(self, task: str, naics_code: str):
        """Get required PPE for task"""
        ppe = ['Hard hat', 'Safety glasses', 'Steel-toed boots']  # Base PPE
        
        task_lower = task.lower()
        
        if any(keyword in task_lower for keyword in ['height', 'elevation', 'lifting', 'positioning']):
            ppe.append('Fall protection harness')
        
        if any(keyword in task_lower for keyword in ['glass', 'cutting', 'sharp']):
            ppe.append('Cut-resistant gloves')
        
        if any(keyword in task_lower for keyword in ['noise', 'drilling', 'cutting']):
            ppe.append('Hearing protection')
        
        return ppe
    
    def _get_training_requirements(self, task: str, naics_code: str):
        """Get training requirements for task"""
        training = ['General safety orientation']
        
        task_lower = task.lower()
        
        if any(keyword in task_lower for keyword in ['height', 'elevation']):
            training.append('Fall protection training')
        
        if any(keyword in task_lower for keyword in ['lifting', 'crane', 'hoist']):
            training.append('Rigging and lifting safety')
        
        if any(keyword in task_lower for keyword in ['glass', 'glazing']):
            training.append('Glass handling procedures')
        
        return training

# Add JHSA endpoints to your Safety API
def add_jhsa_endpoints_to_safety_api(app, safety_api):
    """Add JHSA endpoints to existing Safety API"""
    
    jhsa_generator = JHSAGenerator(safety_api)
    
    @app.post("/generate-jhsa")
    async def generate_jhsa(request: dict):
        """
        Generate JHSA template based on NAICS code and job details
        
        Request format:
        {
            "naics_code": "23815",
            "job_title": "Curtain Wall Installation", 
            "custom_tasks": ["Optional list of custom tasks"]
        }
        """
        naics_code = request.get("naics_code")
        job_title = request.get("job_title")
        custom_tasks = request.get("custom_tasks")
        
        if not naics_code or not job_title:
            raise HTTPException(status_code=400, detail="Missing required fields: naics_code, job_title")
        
        jhsa_template = jhsa_generator.generate_jhsa_template(naics_code, job_title, custom_tasks)
        
        return {
            "success": True,
            "jhsa_template": jhsa_template,
            "osha_compliance": "Based on OSHA 3071 methodology"
        }
    
    @app.get("/jhsa-trades")
    async def get_supported_trades():
        """Get list of supported trades for JHSA generation"""
        return {
            "supported_trades": [
                {"naics_code": "23815", "trade_name": "Glass and Glazing Contractors"},
                {"naics_code": "23813", "trade_name": "Framing Contractors"}, 
                {"naics_code": "23816", "trade_name": "Roofing Contractors"}
            ],
            "can_generate_custom": True,
            "based_on": "OSHA 3071 Job Hazard Analysis methodology"
        }

if __name__ == "__main__":
    # Test JHSA generation
    from safety_api_server import SafetyIntelligenceAPI
    
    safety_api = SafetyIntelligenceAPI()
    jhsa_gen = JHSAGenerator(safety_api)
    
    # Test glass and glazing JHSA
    template = jhsa_gen.generate_jhsa_template(
        "23815", 
        "Curtain Wall Installation - Multi-Story Building",
        ["Material delivery", "Glass panel lifting", "Installation and securing", "Quality inspection"]
    )
    
    print("=== JHSA TEMPLATE GENERATED ===")
    print(json.dumps(template, indent=2))
