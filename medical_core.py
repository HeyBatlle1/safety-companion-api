from typing import List, Dict, Any, Literal

# Define Pydantic-style input for type hinting, actual validation will be in FastAPI layer
class TraumaAssessmentInput:
    mechanismOfInjury: str
    reportedSymptoms: List[str]
    conscious: bool
    age: int = None # Optional
    gender: Literal["male", "female", "other", "unknown"] = None # Optional
    obviousBleeding: bool = None # Optional

# Define Pydantic-style output for type hinting
class TraumaAssessmentOutput:
    severity_level: Literal["critical", "serious", "moderate", "minor", "unknown"]
    immediate_actions: List[str]
    assessment_steps: List[str]
    red_flags: List[str]
    next_steps: List[str]

def perform_trauma_assessment(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs a generic trauma assessment based on patient data.
    Input is a dictionary, expected to match TraumaAssessmentInput structure.
    Output is a dictionary, matching TraumaAssessmentOutput structure.
    """
    # Basic validation (FastAPI with Pydantic will handle more robust validation at API layer)
    if not all(key in patient_data for key in ["mechanismOfInjury", "reportedSymptoms", "conscious"]):
        # In a real MCP, this might return a structured error or raise a specific exception
        return {
            "severity_level": "unknown",
            "immediate_actions": ["Error: Missing required patient data (mechanismOfInjury, reportedSymptoms, conscious)."],
            "assessment_steps": [],
            "red_flags": ["Missing critical input data."],
            "next_steps": ["Re-submit with complete data."]
        }

    mechanism = patient_data.get("mechanismOfInjury", "").lower()
    symptoms = [s.lower() for s in patient_data.get("reportedSymptoms", [])]
    is_conscious = patient_data.get("conscious", False)
    has_obvious_bleeding = patient_data.get("obviousBleeding", False)

    severity_level: Literal["critical", "serious", "moderate", "minor", "unknown"] = "unknown"
    immediate_actions: List[str] = ["Ensure scene safety.", "Call for emergency medical services if possible and not already done."]
    assessment_steps: List[str] = [
        "Check for responsiveness (AVPU: Alert, Verbal, Painful, Unresponsive).",
        "Assess Airway (A): Is it clear? Any obstructions? Consider C-spine immobilization if trauma mechanism suggests.",
        "Assess Breathing (B): Rate, depth, effort. Look for chest rise and fall. Check for cyanosis.",
        "Assess Circulation (C): Check for major bleeding. Check pulse (rate, rhythm, strength). Check skin color, temperature, and capillary refill.",
        "Assess Disability (D): Neurological status (e.g., GCS if trained, pupil response, orientation).",
        "Expose and Examine (E): Systematically check for injuries from head to toe, maintaining spinal precautions if suspected neck/back injury. Keep patient warm.",
    ]
    red_flags: List[str] = [
        "Unresponsiveness or significantly altered mental status.",
        "Difficulty breathing, gasping, or no breathing.",
        "Absent or very weak pulse, signs of shock (pale, cool, clammy skin).",
        "Severe, uncontrolled external bleeding.",
        "Penetrating trauma to head, neck, chest, or abdomen.",
        "Suspected spinal injury (e.g., fall from height, diving accident, high-speed MVA).",
        "Open fractures or severe deformities."
    ]
    next_steps: List[str] = [
        "Reassess ABCDEs frequently (e.g., every 5 minutes for critical, 15 for stable).",
        "Treat life-threatening injuries found during assessment immediately (e.g., control major bleeding, basic airway maneuvers, CPR if indicated).",
        "Maintain body temperature (prevent hypothermia).",
        "Gather SAMPLE history if possible (Signs/Symptoms, Allergies, Medications, Past medical history, Last oral intake, Events leading to injury).",
        "Prepare for transport or await arrival of higher-level care.",
    ]

    if not is_conscious:
        severity_level = "critical"
        immediate_actions.insert(1, "If not breathing or only gasping, begin CPR immediately if trained and appropriate.")
        red_flags.append("Patient is unconscious.")
    elif has_obvious_bleeding or "severe bleeding" in symptoms:
        severity_level = "critical" if "arterial" in mechanism else "serious"
        immediate_actions.insert(1, "Apply direct pressure to any sites of major bleeding. Elevate if possible. Consider tourniquet for life-threatening limb hemorrhage.")
        red_flags.append("Obvious or reported severe bleeding.")
    elif any(s in symptoms for s in ["difficulty breathing", "shortness of breath", "no breathing", "gasping"]):
        severity_level = "critical"
        immediate_actions.insert(1, "Ensure airway is open. Assist ventilations if necessary and trained.")
        red_flags.append("Reported difficulty breathing or abnormal breathing pattern.")
    elif "fall from height" in mechanism or "motor vehicle accident" in mechanism or "diving accident" in mechanism:
        severity_level = "serious" # Could be critical depending on other factors
        immediate_actions.append("Maintain spinal immobilization if suspected neck/back injury.")
        red_flags.append("High-risk mechanism of injury (potential for internal or spinal injuries).")
    else:
        severity_level = "moderate" # Default for conscious patient without immediate critical signs

    if "chest pain" in symptoms:
        red_flags.append("Reported chest pain - consider cardiac or significant thoracic trauma.")
        if severity_level not in ["critical", "serious"]: severity_level = "serious"

    return {
        "severity_level": severity_level,
        "immediate_actions": immediate_actions,
        "assessment_steps": assessment_steps,
        "red_flags": red_flags,
        "next_steps": next_steps,
    }

# Example usage (for testing this module directly)
if __name__ == "__main__":
    test_data_critical = {
        "mechanismOfInjury": "Fall from 20ft ladder",
        "reportedSymptoms": ["unresponsive", "visible head wound"],
        "conscious": False,
        "obviousBleeding": True
    }
    result_critical = perform_trauma_assessment(test_data_critical)
    print("--- Critical Case ---")
    for key, value in result_critical.items():
        print(f"{key}: {value}")

    test_data_moderate = {
        "mechanismOfInjury": "Twisted ankle on hike",
        "reportedSymptoms": ["pain in ankle", "swelling"],
        "conscious": True,
        "obviousBleeding": False
    }
    result_moderate = perform_trauma_assessment(test_data_moderate)
    print("\n--- Moderate Case ---")
    for key, value in result_moderate.items():
        print(f"{key}: {value}")

    test_data_missing = {
        "mechanismOfInjury": "Unknown",
        "reportedSymptoms": ["dizzy"]
        # "conscious" is missing
    }
    result_missing = perform_trauma_assessment(test_data_missing)
    print("\n--- Missing Data Case ---")
    for key, value in result_missing.items():
        print(f"{key}: {value}")
