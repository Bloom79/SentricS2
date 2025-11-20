"""
Modello Unico Semplificato Generator
Generates Italian simplified connection forms for photovoltaic plants up to 200 kW
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AuthorizationType(str, Enum):
    """Authorization type based on plant power"""
    CILA = "CILA"  # <20 kW
    PAS = "PAS"  # 20-200 kW
    AU = "AU"  # >200 kW


class ConnectionType(str, Enum):
    """Grid connection type"""
    NEW = "new"
    EXISTING_MODIFICATION = "existing_modification"
    POWER_INCREASE = "power_increase"


class ModelloUnicoGenerator:
    """
    Service for generating Modello Unico Semplificato forms

    Legal Reference:
    - D.M. 297/2022 (extended to 200 kW from 50 kW)
    - Updated templates effective May 30, 2025
    """

    # Deadlines
    GRID_OPERATOR_RESPONSE_DAYS = 20  # Working days for Part I response
    CONNECTION_ACTIVATION_DAYS = 10  # Working days after Part II

    @staticmethod
    def determine_authorization_type(power_kw: float) -> AuthorizationType:
        """
        Determine required authorization type based on plant power

        Args:
            power_kw: Plant nominal power in kW

        Returns:
            Authorization type required
        """
        if power_kw < 20:
            return AuthorizationType.CILA
        elif power_kw <= 200:
            return AuthorizationType.PAS
        else:
            return AuthorizationType.AU

    @staticmethod
    def generate_part_1(
        plant_data: Dict[str, Any],
        owner_data: Dict[str, Any],
        connection_type: ConnectionType = ConnectionType.NEW
    ) -> Dict[str, Any]:
        """
        Generate Modello Unico - Part I (before work starts)

        Part I includes:
        - Connection request
        - IBAN for payments
        - Compliance declarations
        - Single-line electrical diagram
        - Identity documents
        - Delegation (if applicable)

        Args:
            plant_data: Plant technical data
            owner_data: Owner/producer data
            connection_type: Type of connection

        Returns:
            Dictionary with Part I form data
        """
        power_kw = plant_data.get("power_kw", 0)
        authorization_type = ModelloUnicoGenerator.determine_authorization_type(power_kw)

        # Calculate expected response date
        submission_date = datetime.now()
        expected_response = submission_date + timedelta(days=ModelloUnicoGenerator.GRID_OPERATOR_RESPONSE_DAYS)

        part_1_data = {
            "form_type": "Modello Unico Semplificato - Parte I",
            "form_version": "2025-05-30",
            "submission_date": submission_date.strftime("%Y-%m-%d"),
            "expected_response_date": expected_response.strftime("%Y-%m-%d"),

            # Section 1: Producer/Owner Data
            "section_1_producer": {
                "denomination": owner_data.get("company_name") or owner_data.get("name"),
                "fiscal_code": owner_data.get("fiscal_code"),
                "vat_number": owner_data.get("vat_number"),
                "legal_address": owner_data.get("legal_address"),
                "city": owner_data.get("city"),
                "province": owner_data.get("province"),
                "postal_code": owner_data.get("postal_code"),
                "pec_email": owner_data.get("pec_email"),
                "phone": owner_data.get("phone"),
                "legal_representative": owner_data.get("legal_representative"),
            },

            # Section 2: Plant Location and Technical Data
            "section_2_plant": {
                "plant_name": plant_data.get("name"),
                "installation_address": plant_data.get("address"),
                "city": plant_data.get("city"),
                "province": plant_data.get("province"),
                "postal_code": plant_data.get("postal_code"),
                "cadastral_data": plant_data.get("cadastral_data", {}),
                "coordinates": {
                    "latitude": plant_data.get("latitude"),
                    "longitude": plant_data.get("longitude")
                },
                "nominal_power_kw": power_kw,
                "num_modules": plant_data.get("num_modules"),
                "num_inverters": plant_data.get("num_inverters"),
                "module_manufacturer": plant_data.get("module_manufacturer"),
                "module_model": plant_data.get("module_model"),
                "inverter_manufacturer": plant_data.get("inverter_manufacturer"),
                "inverter_model": plant_data.get("inverter_model"),
                "installation_type": plant_data.get("installation_type", "rooftop"),  # rooftop, ground, facade
            },

            # Section 3: Connection Request
            "section_3_connection": {
                "connection_type": connection_type.value,
                "existing_pod": plant_data.get("existing_pod"),
                "voltage_level": plant_data.get("voltage_level", "BT"),  # BT (low), MT (medium)
                "connection_point": plant_data.get("connection_point"),
                "requested_connection_power_kw": power_kw,
                "iban": owner_data.get("iban"),
            },

            # Section 4: Authorization Type
            "section_4_authorization": {
                "type": authorization_type.value,
                "description": ModelloUnicoGenerator._get_authorization_description(authorization_type),
                "authority": "Comune" if authorization_type in [AuthorizationType.CILA, AuthorizationType.PAS] else "Regione",
                "estimated_timeline": ModelloUnicoGenerator._get_authorization_timeline(authorization_type),
            },

            # Section 5: Professional Data (Technician)
            "section_5_professional": {
                "name": plant_data.get("technician_name"),
                "fiscal_code": plant_data.get("technician_fiscal_code"),
                "professional_order": plant_data.get("technician_order", "Ordine Ingegneri"),
                "order_province": plant_data.get("technician_order_province"),
                "order_number": plant_data.get("technician_order_number"),
                "pec_email": plant_data.get("technician_pec"),
                "phone": plant_data.get("technician_phone"),
            },

            # Section 6: Declarations
            "section_6_declarations": {
                "declares_ownership": True,
                "declares_compliance": True,
                "declares_no_landscape_restrictions": plant_data.get("no_landscape_restrictions", False),
                "declares_building_compliance": plant_data.get("building_compliance", True),
                "accepts_terms": True,
            },

            # Section 7: Required Documents
            "section_7_documents": {
                "required": [
                    "Single-line electrical diagram (signed by qualified technician)",
                    "Identity document (front and back)",
                    "IBAN certificate",
                    "Delegation (if applicable)",
                    "Cadastral map (not older than 6 months)",
                    "Latest electricity bill (if existing POD)",
                ],
                "optional": [
                    "Building ownership certificate",
                    "Rental agreement (if rented property)",
                    "Condominium authorization (if applicable)",
                ]
            },

            # Section 8: Submission Details
            "section_8_submission": {
                "dso_name": plant_data.get("dso_name", "E-Distribuzione"),
                "submission_method": "Online portal",
                "portal_url": ModelloUnicoGenerator._get_dso_portal_url(plant_data.get("dso_name")),
                "tracking_number": None,  # Will be filled after submission
                "status": "draft",
            },

            # Metadata
            "metadata": {
                "form_generated_at": datetime.now().isoformat(),
                "generated_by": "SentricS2 Platform",
                "version": "1.0",
            }
        }

        return part_1_data

    @staticmethod
    def generate_part_2(
        part_1_data: Dict[str, Any],
        commissioning_data: Dict[str, Any],
        test_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate Modello Unico - Part II (after work completion)

        Part II includes:
        - Commissioning date
        - Final electrical measurements
        - Compliance certifications
        - Test reports
        - As-built documentation

        Args:
            part_1_data: Previously submitted Part I data
            commissioning_data: Commissioning and completion data
            test_results: Electrical test results

        Returns:
            Dictionary with Part II form data
        """
        # Calculate expected connection date
        submission_date = datetime.now()
        expected_connection = submission_date + timedelta(days=ModelloUnicoGenerator.CONNECTION_ACTIVATION_DAYS)

        part_2_data = {
            "form_type": "Modello Unico Semplificato - Parte II",
            "form_version": "2025-05-30",
            "submission_date": submission_date.strftime("%Y-%m-%d"),
            "expected_connection_date": expected_connection.strftime("%Y-%m-%d"),

            # Reference to Part I
            "part_1_reference": {
                "tracking_number": part_1_data.get("section_8_submission", {}).get("tracking_number"),
                "submission_date": part_1_data.get("submission_date"),
            },

            # Section 1: Work Completion
            "section_1_completion": {
                "work_start_date": commissioning_data.get("work_start_date"),
                "work_end_date": commissioning_data.get("work_end_date"),
                "commissioning_date": commissioning_data.get("commissioning_date"),
                "installer_company": commissioning_data.get("installer_company"),
                "installer_fiscal_code": commissioning_data.get("installer_fiscal_code"),
            },

            # Section 2: Final Technical Data
            "section_2_final_technical": {
                "installed_power_kw": commissioning_data.get("installed_power_kw"),
                "num_modules_installed": commissioning_data.get("num_modules_installed"),
                "num_inverters_installed": commissioning_data.get("num_inverters_installed"),
                "meter_serial_number": commissioning_data.get("meter_serial_number"),
                "meter_manufacturer": commissioning_data.get("meter_manufacturer"),
                "meter_model": commissioning_data.get("meter_model"),
                "meter_installation_date": commissioning_data.get("meter_installation_date"),
            },

            # Section 3: Electrical Test Results
            "section_3_tests": {
                "insulation_test_passed": test_results.get("insulation_test_passed"),
                "insulation_test_value_mohm": test_results.get("insulation_test_value"),
                "ground_test_passed": test_results.get("ground_test_passed"),
                "ground_resistance_ohm": test_results.get("ground_resistance"),
                "protection_device_test_passed": test_results.get("protection_test_passed"),
                "inverter_test_passed": test_results.get("inverter_test_passed"),
                "grid_connection_test_passed": test_results.get("grid_connection_test_passed"),
                "all_tests_passed": all([
                    test_results.get("insulation_test_passed"),
                    test_results.get("ground_test_passed"),
                    test_results.get("protection_test_passed"),
                    test_results.get("inverter_test_passed"),
                    test_results.get("grid_connection_test_passed"),
                ]),
            },

            # Section 4: Compliance Declarations
            "section_4_declarations": {
                "declaration_of_conformity_available": commissioning_data.get("conformity_declaration_available"),
                "declaration_number": commissioning_data.get("conformity_declaration_number"),
                "declaration_date": commissioning_data.get("conformity_declaration_date"),
                "technician_signature": commissioning_data.get("technician_name"),
                "technician_order_number": commissioning_data.get("technician_order_number"),
            },

            # Section 5: Required Documents for Part II
            "section_5_documents": {
                "required": [
                    "Electrical compliance declaration (DiCo)",
                    "Test report with measurements",
                    "Protection device calibration certificate",
                    "As-built electrical diagram",
                    "Meter installation certificate",
                    "Photographic documentation of installation",
                ],
                "optional": [
                    "Structural engineer certification (if needed)",
                    "Fire safety certification (if applicable)",
                ]
            },

            # Section 6: Connection Activation Request
            "section_6_activation": {
                "requested_activation_date": commissioning_data.get("requested_activation_date"),
                "emergency_contact_name": commissioning_data.get("emergency_contact_name"),
                "emergency_contact_phone": commissioning_data.get("emergency_contact_phone"),
                "declares_plant_ready": True,
                "declares_safety_compliant": True,
            },

            # Section 7: Submission Details
            "section_7_submission": {
                "dso_name": part_1_data.get("section_8_submission", {}).get("dso_name"),
                "tracking_number": None,  # Will be filled after submission
                "status": "draft",
            },

            # Metadata
            "metadata": {
                "form_generated_at": datetime.now().isoformat(),
                "generated_by": "SentricS2 Platform",
                "version": "1.0",
            }
        }

        return part_2_data

    @staticmethod
    def generate_submission_checklist(part_number: int, plant_power_kw: float) -> Dict[str, Any]:
        """
        Generate submission checklist for Modello Unico

        Args:
            part_number: Part number (1 or 2)
            plant_power_kw: Plant power in kW

        Returns:
            Dictionary with checklist
        """
        authorization_type = ModelloUnicoGenerator.determine_authorization_type(plant_power_kw)

        if part_number == 1:
            checklist = {
                "part": 1,
                "title": "Modello Unico - Part I Submission Checklist",
                "items": [
                    {
                        "id": 1,
                        "category": "Documents",
                        "task": "Prepare single-line electrical diagram (signed by qualified technician)",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 2,
                        "category": "Documents",
                        "task": "Scan identity document (front and back, valid)",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 3,
                        "category": "Documents",
                        "task": "Obtain IBAN certificate from bank",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 4,
                        "category": "Documents",
                        "task": "Obtain cadastral map (not older than 6 months)",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 5,
                        "category": "Documents",
                        "task": "Get latest electricity bill (if existing POD)",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 6,
                        "category": "Authorization",
                        "task": f"Submit {authorization_type.value} to Comune/Regione",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 7,
                        "category": "Data Entry",
                        "task": "Access DSO portal (E-Distribuzione or other)",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 8,
                        "category": "Data Entry",
                        "task": "Fill in producer/owner data section",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 9,
                        "category": "Data Entry",
                        "task": "Fill in plant technical data section",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 10,
                        "category": "Data Entry",
                        "task": "Fill in connection request section",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 11,
                        "category": "Upload",
                        "task": "Upload all required documents (PDF format)",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 12,
                        "category": "Submission",
                        "task": "Review all data for accuracy",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 13,
                        "category": "Submission",
                        "task": "Submit Part I and receive tracking number",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 14,
                        "category": "Follow-up",
                        "task": "Monitor DSO response (20 working days deadline)",
                        "completed": False,
                        "required": True
                    },
                ],
                "timeline": "Expected DSO response: 20 working days",
                "next_step": "Wait for DSO approval before starting work"
            }
        elif part_number == 2:
            checklist = {
                "part": 2,
                "title": "Modello Unico - Part II Submission Checklist",
                "items": [
                    {
                        "id": 1,
                        "category": "Work Completion",
                        "task": "Complete plant installation",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 2,
                        "category": "Testing",
                        "task": "Perform insulation test (>1 MΩ required)",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 3,
                        "category": "Testing",
                        "task": "Perform ground resistance test (<20 Ω required)",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 4,
                        "category": "Testing",
                        "task": "Test protection devices (correct operation)",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 5,
                        "category": "Testing",
                        "task": "Test inverter functionality and grid compliance",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 6,
                        "category": "Testing",
                        "task": "Perform grid connection test",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 7,
                        "category": "Documentation",
                        "task": "Obtain electrical compliance declaration (DiCo)",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 8,
                        "category": "Documentation",
                        "task": "Prepare test report with all measurements",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 9,
                        "category": "Documentation",
                        "task": "Update as-built electrical diagram",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 10,
                        "category": "Documentation",
                        "task": "Take photographic documentation of installation",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 11,
                        "category": "Meter",
                        "task": "Install production meter",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 12,
                        "category": "Meter",
                        "task": "Record meter serial number and initial reading",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 13,
                        "category": "Data Entry",
                        "task": "Access DSO portal with Part I tracking number",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 14,
                        "category": "Data Entry",
                        "task": "Fill in work completion and commissioning data",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 15,
                        "category": "Upload",
                        "task": "Upload all Part II required documents",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 16,
                        "category": "Submission",
                        "task": "Submit Part II and receive tracking number",
                        "completed": False,
                        "required": True
                    },
                    {
                        "id": 17,
                        "category": "Follow-up",
                        "task": "Monitor connection activation (10 working days)",
                        "completed": False,
                        "required": True
                    },
                ],
                "timeline": "Expected connection: 10 working days from Part II submission",
                "next_step": "Plant will be connected and can start production"
            }
        else:
            raise ValueError("part_number must be 1 or 2")

        return checklist

    @staticmethod
    def _get_authorization_description(auth_type: AuthorizationType) -> str:
        """Get description of authorization type"""
        descriptions = {
            AuthorizationType.CILA: "Comunicazione Inizio Lavori Asseverata - Simplified communication for plants <20 kW",
            AuthorizationType.PAS: "Procedura Abilitativa Semplificata - Simplified authorization for plants 20-200 kW",
            AuthorizationType.AU: "Autorizzazione Unica - Single authorization for plants >200 kW"
        }
        return descriptions.get(auth_type, "Unknown authorization type")

    @staticmethod
    def _get_authorization_timeline(auth_type: AuthorizationType) -> str:
        """Get timeline for authorization"""
        timelines = {
            AuthorizationType.CILA: "Immediate (communication only)",
            AuthorizationType.PAS: "30 days (tacit approval if no response)",
            AuthorizationType.AU: "90-180 days (requires formal approval)"
        }
        return timelines.get(auth_type, "Unknown timeline")

    @staticmethod
    def _get_dso_portal_url(dso_name: Optional[str]) -> str:
        """Get DSO portal URL"""
        portals = {
            "E-Distribuzione": "https://www.e-distribuzione.it/",
            "Enel": "https://www.enel.it/",
            "Areti": "https://www.areti.it/",
            "IRETI": "https://www.ireti.it/",
            "Unareti": "https://www.unareti.it/",
        }
        return portals.get(dso_name, "https://www.e-distribuzione.it/")


# Export service instance
modello_unico_generator = ModelloUnicoGenerator()
