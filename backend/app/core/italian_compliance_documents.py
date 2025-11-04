"""
Italian Compliance Documents - Reference Data
Comprehensive list of documents required for compliance in Italian renewable energy sector
"""

from typing import Dict, List
from enum import Enum


class ComplianceEntity(str, Enum):
    """Italian compliance entities"""
    GSE = "GSE"
    TERNA = "Terna"
    DSO = "DSO"
    ADM = "ADM"
    COMUNE = "Comune"
    CER = "CER"


class DocumentCategory(str, Enum):
    """Document categories"""
    INITIAL_REGISTRATION = "initial_registration"
    ANNUAL_RECURRING = "annual_recurring"
    COMPLIANCE = "compliance"
    CONTRACT = "contract"
    TECHNICAL = "technical"
    FINANCIAL = "financial"
    LEGAL = "legal"


# Comprehensive document mapping by entity and category
ITALIAN_COMPLIANCE_DOCUMENTS: Dict[str, Dict[str, List[str]]] = {
    ComplianceEntity.GSE: {
        DocumentCategory.INITIAL_REGISTRATION: [
            "RID Application Form",
            "Plant Technical Specifications",
            "Anti-Mafia Declaration",
            "Company Registration Documents",
            "Tax Code Certificate",
            "VAT Registration",
            "PEC Email Certificate",
            "Bank Account Details",
            "Authorization to Act",
            "Power of Attorney",
        ],
        DocumentCategory.ANNUAL_RECURRING: [
            "Fuel Mix Disclosure",
            "Anti-Mafia Declaration",
            "Consumption Declaration",
            "MFA Update Form",
            "Production Data Reports",
            "Meter Configuration Updates",
        ],
        DocumentCategory.CONTRACT: [
            "RID Contract",
            "Contract Modifications",
            "Incentive Application Forms",
            "Annual Reconciliation Documents",
        ],
    },
    ComplianceEntity.TERNA: {
        DocumentCategory.INITIAL_REGISTRATION: [
            "Plant Registration Form",
            "Technical Connection Document (TICA)",
            "Electrical Diagram",
            "Production Unit Specifications",
            "Meter Configuration Data",
            "CENSIMP Code Application",
            "Plant Technical Sheet",
        ],
        DocumentCategory.COMPLIANCE: [
            "Technical Data Updates",
            "Production Unit Modifications",
            "Capacity Change Declarations",
            "Annual Data Reconciliation",
            "Plant Census Updates",
            "Technical Certification",
            "Connection Point Documentation",
        ],
    },
    ComplianceEntity.DSO: {
        DocumentCategory.INITIAL_REGISTRATION: [
            "TICA Request Form",
            "Site Plan",
            "Electrical Diagrams",
            "Authorization Documents",
            "Technical Specifications",
            "Connection Point Agreement",
        ],
        DocumentCategory.COMPLIANCE: [
            "Meter Calibration Certificate",
            "Protection System Verification",
            "Technical Documentation Updates",
            "Work Completion Declaration",
            "Connection Activation Request",
            "Meter Test Reports",
            "Protection System Test Reports",
            "Safety Compliance Certificates",
        ],
    },
    ComplianceEntity.ADM: {
        DocumentCategory.INITIAL_REGISTRATION: [
            "UTF License Application",
            "Photo of Meter Group",
            "Workshop Declaration",
            "General Site Plan",
            "Technical Report",
            "Single-Line Electrical Diagram",
            "Compliance Declaration",
        ],
        DocumentCategory.ANNUAL_RECURRING: [
            "Consumption Declaration",
            "License Fee Payment Receipt",
            "Workshop License Renewal",
            "Annual Production Reports",
        ],
        DocumentCategory.COMPLIANCE: [
            "Workshop Operating License",
            "Annual Compliance Certificate",
            "Inspection Reports",
        ],
    },
    ComplianceEntity.COMUNE: {
        DocumentCategory.INITIAL_REGISTRATION: [
            "CILA Form (<20kW)",
            "PAS Application (20-200kW)",
            "AU Application (>200kW)",
            "Technical Report",
            "Site Plan",
            "Project Drawings",
            "Environmental Impact Assessment",
            "Landscape Impact Assessment",
        ],
        DocumentCategory.ANNUAL_RECURRING: [
            "IMU/TASI Property Tax Declaration",
            "Building Compliance Certificates",
            "Environmental Compliance Reports",
            "Periodic Inspection Reports",
        ],
    },
    ComplianceEntity.CER: {
        DocumentCategory.INITIAL_REGISTRATION: [
            "CER Registration Form",
            "Legal Entity Documents",
            "Member List",
            "Member Agreements",
            "Boundary Definition",
            "Technical Specifications",
        ],
        DocumentCategory.FINANCIAL: [
            "PNRR Application Form",
            "Investment Plan",
            "Feasibility Study",
            "Technical-Economic Report",
            "Environmental Impact Assessment",
            "Social Impact Assessment",
        ],
        DocumentCategory.ANNUAL_RECURRING: [
            "Annual Financial Report",
            "Compliance Report",
            "Member Summary",
            "Energy Sharing Reports",
            "Incentive Distribution Reports",
        ],
        DocumentCategory.COMPLIANCE: [
            "Monthly Energy Data",
            "Member Activity Reports",
            "Energy Transaction Records",
        ],
    },
}


def get_required_documents(entity: str, category: str = None) -> List[str]:
    """
    Get required documents for a compliance entity
    
    Args:
        entity: Compliance entity (GSE, Terna, DSO, ADM, Comune, CER)
        category: Optional document category filter
    
    Returns:
        List of required document names
    """
    entity_docs = ITALIAN_COMPLIANCE_DOCUMENTS.get(entity, {})
    
    if category:
        return entity_docs.get(category, [])
    
    # Return all documents for the entity
    all_docs = []
    for docs in entity_docs.values():
        all_docs.extend(docs)
    return list(set(all_docs))  # Remove duplicates


def get_documents_by_requirement_type(requirement_type: str) -> List[str]:
    """
    Get documents based on requirement type
    
    Args:
        requirement_type: Type of requirement (e.g., 'RID_ACTIVATION', 'FUEL_MIX', etc.)
    
    Returns:
        List of required document names
    """
    # Map requirement types to documents
    requirement_mapping = {
        "RID_ACTIVATION": get_required_documents(ComplianceEntity.GSE, DocumentCategory.INITIAL_REGISTRATION),
        "FUEL_MIX": ["Fuel Mix Disclosure"],
        "ANTI_MAFIA": ["Anti-Mafia Declaration"],
        "GAUDI_REGISTRATION": get_required_documents(ComplianceEntity.TERNA, DocumentCategory.INITIAL_REGISTRATION),
        "TICA_REQUEST": get_required_documents(ComplianceEntity.DSO, DocumentCategory.INITIAL_REGISTRATION),
        "UTF_LICENSE": get_required_documents(ComplianceEntity.ADM, DocumentCategory.INITIAL_REGISTRATION),
        "CONSUMPTION_DECLARATION": ["Consumption Declaration"],
        "METER_CALIBRATION": ["Meter Calibration Certificate"],
        "CER_REGISTRATION": get_required_documents(ComplianceEntity.CER, DocumentCategory.INITIAL_REGISTRATION),
        "PNRR_APPLICATION": get_required_documents(ComplianceEntity.CER, DocumentCategory.FINANCIAL),
    }
    
    return requirement_mapping.get(requirement_type, [])


def get_all_documents() -> Dict[str, List[str]]:
    """
    Get all documents organized by entity
    
    Returns:
        Dictionary mapping entity names to lists of documents
    """
    result = {}
    for entity, categories in ITALIAN_COMPLIANCE_DOCUMENTS.items():
        result[entity.value] = get_required_documents(entity.value)
    return result

