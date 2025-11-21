"""
Terna GAUDÌ (Gestione Anagrafica Unica Degli Impianti) Integration Client
Handles plant registration and CENSIMP code management
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PlantStatus(str, Enum):
    """Plant registration status in GAUDÌ"""
    DRAFT = "draft"
    REGISTERED = "registered"
    VALIDATED = "validated"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DECOMMISSIONED = "decommissioned"


class PlantType(str, Enum):
    """Types of power plants"""
    PHOTOVOLTAIC = "photovoltaic"
    WIND = "wind"
    HYDRO = "hydro"
    BIOMASS = "biomass"
    HYBRID = "hybrid"


class ConnectionVoltage(str, Enum):
    """Grid connection voltage levels"""
    BT = "BT"  # Bassa Tensione (Low Voltage) < 1 kV
    MT = "MT"  # Media Tensione (Medium Voltage) 1-35 kV
    AT = "AT"  # Alta Tensione (High Voltage) > 35 kV


class TernaGaudiClient:
    """
    Client for Terna GAUDÌ portal integration

    Features:
    - Producer registration
    - Plant registration
    - CENSIMP code management
    - Production data submission
    - Data reconciliation with DSO

    Legal Requirement: All plants must be registered within 30 days of grid connection
    Penalty: €1,000-10,000 for non-compliance

    Portal: https://gaudi.terna.it/
    """

    PORTAL_URL = "https://gaudi.terna.it/"
    REGISTRATION_DEADLINE_DAYS = 30  # From grid connection
    DSO_VALIDATION_DAYS = 15  # Working days for DSO validation

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        test_mode: bool = True
    ):
        """
        Initialize Terna GAUDÌ client

        Args:
            client_id: GAUDÌ API client ID (if available)
            client_secret: GAUDÌ API client secret
            test_mode: Use test/mock mode (default True)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.test_mode = test_mode
        self.access_token = None
        self.token_expiry = None

        logger.info(f"Terna GAUDÌ Client initialized (test_mode={test_mode})")

    def authenticate(
        self,
        fiscal_code: str,
        digital_certificate_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authenticate with Terna GAUDÌ portal

        For plants > 10 MW: Digital certificate required
        For plants < 10 MW: Username/password (SPID) sufficient

        Args:
            fiscal_code: Italian fiscal code
            digital_certificate_path: Path to digital certificate (.p12 file)

        Returns:
            Authentication result
        """
        if self.test_mode:
            self.access_token = f"mock_gaudi_token_{fiscal_code}_{datetime.now().timestamp()}"
            self.token_expiry = datetime.now() + timedelta(hours=8)

            return {
                "authenticated": True,
                "fiscal_code": fiscal_code,
                "access_token": self.access_token,
                "token_expiry": self.token_expiry.isoformat(),
                "portal_url": self.PORTAL_URL,
                "test_mode": True
            }

        # Production implementation
        raise NotImplementedError("Production Terna GAUDÌ authentication required")

    def register_producer(
        self,
        producer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register producer/owner in GAUDÌ system

        Required data:
        - Denomination/company name
        - Fiscal code / VAT number
        - Legal address
        - PEC email
        - Legal representative

        Args:
            producer_data: Producer registration data

        Returns:
            Registration confirmation with producer ID
        """
        self._ensure_authenticated()

        required_fields = ["company_name", "fiscal_code", "legal_address", "pec_email"]
        for field in required_fields:
            if field not in producer_data:
                raise ValueError(f"Missing required field: {field}")

        if self.test_mode:
            producer_id = f"PROD-{datetime.now().timestamp():.0f}"

            return {
                "success": True,
                "producer_id": producer_id,
                "company_name": producer_data["company_name"],
                "fiscal_code": producer_data["fiscal_code"],
                "registration_date": datetime.now().isoformat(),
                "status": "active",
                "test_mode": True
            }

        raise NotImplementedError("Production Terna GAUDÌ API integration required")

    def register_plant(
        self,
        producer_id: str,
        plant_data: Dict[str, Any],
        grid_connection_date: datetime
    ) -> Dict[str, Any]:
        """
        Register plant in GAUDÌ and obtain CENSIMP code

        CRITICAL: Must be done within 30 days of grid connection

        Required data:
        - Plant denomination
        - Installation address
        - Coordinates (latitude, longitude)
        - Nominal power (kW)
        - Plant type
        - POD code
        - Connection voltage level

        Args:
            producer_id: Producer ID from previous registration
            plant_data: Plant technical data
            grid_connection_date: Date of grid connection

        Returns:
            Registration confirmation with CENSIMP code
        """
        self._ensure_authenticated()

        # Check deadline compliance
        days_since_connection = (datetime.now() - grid_connection_date).days
        if days_since_connection > self.REGISTRATION_DEADLINE_DAYS:
            logger.warning(
                f"Plant registration exceeds 30-day deadline: "
                f"{days_since_connection} days since connection. "
                f"Risk of penalties €1,000-10,000"
            )

        required_fields = [
            "name", "address", "latitude", "longitude",
            "power_kw", "plant_type", "pod_code", "voltage_level"
        ]
        for field in required_fields:
            if field not in plant_data:
                raise ValueError(f"Missing required field: {field}")

        if self.test_mode:
            # Generate mock CENSIMP code
            censimp_code = f"CENSIMP{datetime.now().year}{int(datetime.now().timestamp()) % 100000:05d}"

            return {
                "success": True,
                "producer_id": producer_id,
                "plant_id": f"PLANT-{datetime.now().timestamp():.0f}",
                "censimp_code": censimp_code,
                "plant_name": plant_data["name"],
                "power_kw": plant_data["power_kw"],
                "plant_type": plant_data["plant_type"],
                "registration_date": datetime.now().isoformat(),
                "grid_connection_date": grid_connection_date.isoformat(),
                "days_since_connection": days_since_connection,
                "deadline_compliant": days_since_connection <= self.REGISTRATION_DEADLINE_DAYS,
                "status": PlantStatus.REGISTERED.value,
                "next_steps": [
                    f"DSO validation required within {self.DSO_VALIDATION_DAYS} working days",
                    "Monitor GAUDÌ portal for validation status",
                    "Resolve any data discrepancies with DSO",
                    "CENSIMP code required for GSE incentive applications"
                ],
                "dso_validation_deadline": (datetime.now() + timedelta(days=self.DSO_VALIDATION_DAYS)).isoformat(),
                "test_mode": True
            }

        raise NotImplementedError("Production Terna GAUDÌ API integration required")

    def update_plant_data(
        self,
        censimp_code: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update plant data in GAUDÌ system

        Required for:
        - Power capacity changes
        - Technical modifications
        - Ownership changes
        - Decommissioning

        Args:
            censimp_code: Plant CENSIMP code
            updates: Dictionary of fields to update

        Returns:
            Update confirmation
        """
        self._ensure_authenticated()

        if self.test_mode:
            return {
                "success": True,
                "censimp_code": censimp_code,
                "updated_fields": list(updates.keys()),
                "update_date": datetime.now().isoformat(),
                "status": "updated",
                "dso_validation_required": True,
                "test_mode": True
            }

        raise NotImplementedError("Production Terna GAUDÌ API integration required")

    def submit_production_data(
        self,
        censimp_code: str,
        period_month: int,
        period_year: int,
        production_kwh: float
    ) -> Dict[str, Any]:
        """
        Submit monthly production data to Terna

        Required for:
        - Production monitoring
        - Grid balancing
        - Statistical reporting

        Args:
            censimp_code: Plant CENSIMP code
            period_month: Month (1-12)
            period_year: Year
            production_kwh: Total monthly production in kWh

        Returns:
            Submission confirmation
        """
        self._ensure_authenticated()

        if self.test_mode:
            return {
                "success": True,
                "censimp_code": censimp_code,
                "period": f"{period_year}-{period_month:02d}",
                "production_kwh": production_kwh,
                "submission_date": datetime.now().isoformat(),
                "status": "accepted",
                "test_mode": True
            }

        raise NotImplementedError("Production Terna GAUDÌ API integration required")

    def check_dso_validation_status(
        self,
        censimp_code: str
    ) -> Dict[str, Any]:
        """
        Check DSO validation status for registered plant

        DSO has 15 working days to validate plant data

        Args:
            censimp_code: Plant CENSIMP code

        Returns:
            Validation status
        """
        self._ensure_authenticated()

        if self.test_mode:
            return {
                "censimp_code": censimp_code,
                "validation_status": "validated",
                "validated_by": "E-Distribuzione",
                "validation_date": datetime.now().isoformat(),
                "discrepancies": [],
                "notes": "All data validated successfully",
                "test_mode": True
            }

        raise NotImplementedError("Production Terna GAUDÌ API integration required")

    def get_plant_details(
        self,
        censimp_code: str
    ) -> Dict[str, Any]:
        """
        Retrieve plant details from GAUDÌ

        Args:
            censimp_code: Plant CENSIMP code

        Returns:
            Plant details from GAUDÌ registry
        """
        self._ensure_authenticated()

        if self.test_mode:
            return {
                "censimp_code": censimp_code,
                "plant_name": "Mock Plant",
                "power_kw": 100.0,
                "plant_type": PlantType.PHOTOVOLTAIC.value,
                "voltage_level": ConnectionVoltage.BT.value,
                "registration_date": "2024-01-15",
                "status": PlantStatus.ACTIVE.value,
                "producer_name": "Mock Producer",
                "address": "Via Roma 1, 00100 Roma RM",
                "coordinates": {
                    "latitude": 41.9028,
                    "longitude": 12.4964
                },
                "test_mode": True
            }

        raise NotImplementedError("Production Terna GAUDÌ API integration required")

    def decommission_plant(
        self,
        censimp_code: str,
        decommissioning_date: datetime,
        reason: str
    ) -> Dict[str, Any]:
        """
        Decommission plant in GAUDÌ system

        Required when:
        - Plant is permanently shut down
        - Plant is dismantled
        - Plant ownership changes

        Args:
            censimp_code: Plant CENSIMP code
            decommissioning_date: Date of decommissioning
            reason: Reason for decommissioning

        Returns:
            Decommissioning confirmation
        """
        self._ensure_authenticated()

        if self.test_mode:
            return {
                "success": True,
                "censimp_code": censimp_code,
                "decommissioning_date": decommissioning_date.isoformat(),
                "reason": reason,
                "status": PlantStatus.DECOMMISSIONED.value,
                "final_production_data_required": True,
                "next_steps": [
                    "Submit final production data",
                    "Notify GSE of decommissioning",
                    "Update DSO connection status",
                    "Complete tax declarations"
                ],
                "test_mode": True
            }

        raise NotImplementedError("Production Terna GAUDÌ API integration required")

    def reconcile_data_with_dso(
        self,
        censimp_code: str,
        dso_name: str
    ) -> Dict[str, Any]:
        """
        Reconcile plant data with Distribution System Operator

        Checks for discrepancies between GAUDÌ and DSO records

        Args:
            censimp_code: Plant CENSIMP code
            dso_name: DSO name (E-Distribuzione, Enel, etc.)

        Returns:
            Reconciliation result
        """
        self._ensure_authenticated()

        if self.test_mode:
            return {
                "censimp_code": censimp_code,
                "dso_name": dso_name,
                "reconciliation_date": datetime.now().isoformat(),
                "status": "reconciled",
                "discrepancies_found": 0,
                "discrepancies": [],
                "gaudi_data_matches_dso": True,
                "test_mode": True
            }

        raise NotImplementedError("Production Terna GAUDÌ API integration required")

    def _ensure_authenticated(self):
        """Ensure client is authenticated with valid token"""
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first")

        if self.token_expiry and datetime.now() > self.token_expiry:
            raise ValueError("Authentication token expired. Re-authenticate required")


# Export client instance
terna_gaudi_client = TernaGaudiClient(test_mode=True)
