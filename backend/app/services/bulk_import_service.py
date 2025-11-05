"""
Bulk Import Service for Assets (especially panels)
Handles CSV parsing, validation, and batch creation
REFACTORED: Reduced complexity by extracting helper methods
"""

from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import csv
import io
import logging

from app.models.asset import Asset
from app.models.plant import Plant
from app.services.base import BaseService

logger = logging.getLogger(__name__)


class BulkImportService(BaseService):
    """Service for bulk importing assets from CSV"""

    REQUIRED_COLUMNS = ["name", "model"]
    OPTIONAL_COLUMNS = [
        "manufacturer",
        "serial_number",
        "location",
        "installation_date",
        "status",
        "power_rating",
        "efficiency",
        "voltage",
        "current",
        "string_number",
        "notes",
    ]

    @staticmethod
    def parse_csv(
        csv_content: str, has_header: bool = True
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Parse CSV content and return rows with errors"""
        errors = []
        rows = []

        try:
            csv_reader = csv.DictReader(io.StringIO(csv_content))

            # Check required columns
            if has_header:
                reader_fieldnames = csv_reader.fieldnames or []
                missing_columns = [
                    col
                    for col in BulkImportService.REQUIRED_COLUMNS
                    if col not in reader_fieldnames
                ]
                if missing_columns:
                    errors.append(f"Missing required columns: {', '.join(missing_columns)}")
                    return rows, errors

            for row_num, row in enumerate(csv_reader, start=2 if has_header else 1):
                # Normalize keys (lowercase, strip spaces)
                normalized_row = {
                    k.lower().strip(): v.strip() if v else None for k, v in row.items()
                }

                # Validate required fields
                row_errors = []
                for col in BulkImportService.REQUIRED_COLUMNS:
                    if not normalized_row.get(col):
                        row_errors.append(f"Row {row_num}: Missing required field '{col}'")

                if row_errors:
                    errors.extend(row_errors)
                    continue

                rows.append({"row_number": row_num, "data": normalized_row})

        except Exception as e:
            errors.append(f"CSV parsing error: {str(e)}")

        return rows, errors

    @staticmethod
    def _validate_string_number(
        string_number: Any, number_of_strings: int
    ) -> Optional[str]:
        """
        Validate string number

        Returns:
            Error message if invalid, None if valid
        """
        if not string_number:
            return None

        try:
            string_num = int(string_number)
            if string_num < 1:
                return "String number must be >= 1"
            if number_of_strings > 0 and string_num > number_of_strings:
                return f"String number must be <= {number_of_strings}"
            return None
        except ValueError:
            return "String number must be a valid integer"

    @staticmethod
    def _validate_installation_date(installation_date: str) -> Optional[str]:
        """
        Validate installation date format

        Returns:
            Error message if invalid, None if valid
        """
        if not installation_date:
            return None

        try:
            datetime.strptime(installation_date, "%Y-%m-%d")
            return None
        except ValueError:
            try:
                datetime.strptime(installation_date, "%Y-%m-%d %H:%M:%S")
                return None
            except ValueError:
                return "Installation date must be in format YYYY-MM-DD or YYYY-MM-DD HH:%M:%S"

    @staticmethod
    def _validate_status(status: str) -> Optional[str]:
        """
        Validate status value

        Returns:
            Error message if invalid, None if valid
        """
        if not status:
            return None

        valid_statuses = ["operational", "maintenance", "offline", "decommissioned"]
        if status not in valid_statuses:
            return f"Status must be one of: {', '.join(valid_statuses)}"
        return None

    @staticmethod
    def _validate_numeric_field(field_name: str, value: Any) -> Optional[str]:
        """
        Validate numeric field

        Returns:
            Error message if invalid, None if valid
        """
        if not value:
            return None

        try:
            float(value)
            return None
        except ValueError:
            return f"{field_name} must be a valid number"

    @staticmethod
    def validate_panel_row(
        row_data: Dict[str, Any],
        array_id: int,
        plant_id: int,
        db: Session,
        tenant_id: str,
        number_of_strings: int = 0,
        panels_per_string: int = 0,
    ) -> List[str]:
        """
        Validate a single panel row

        REFACTORED: Extracted validation logic into helper methods
        Complexity reduced from 16 to ~5
        """
        errors = []

        # Validate string number
        string_error = BulkImportService._validate_string_number(
            row_data.get("string_number"), number_of_strings
        )
        if string_error:
            errors.append(string_error)

        # Validate installation date
        date_error = BulkImportService._validate_installation_date(
            row_data.get("installation_date")
        )
        if date_error:
            errors.append(date_error)

        # Validate status
        status_error = BulkImportService._validate_status(
            row_data.get("status", "operational")
        )
        if status_error:
            errors.append(status_error)

        # Validate numeric fields
        numeric_fields = ["power_rating", "efficiency", "voltage", "current"]
        for field in numeric_fields:
            numeric_error = BulkImportService._validate_numeric_field(
                field, row_data.get(field)
            )
            if numeric_error:
                errors.append(numeric_error)

        return errors

    @staticmethod
    def _verify_plant(
        db: Session, plant_id: int, tenant_id: str
    ) -> Plant:
        """
        Verify plant exists and user has access

        Raises:
            ValueError if plant not found
        """
        plant = BaseService._get_by_id(db, Plant, plant_id, tenant_id)
        if not plant:
            raise ValueError(f"Plant {plant_id} not found")
        return plant

    @staticmethod
    def _load_array_configuration(
        db: Session, array_id: Optional[int], tenant_id: str
    ) -> Tuple[Optional[Asset], int, int, Dict]:
        """
        Load array configuration if array_id provided

        Returns:
            Tuple of (array, number_of_strings, panels_per_string, string_assignments)
        """
        if not array_id:
            return None, 0, 0, {}

        array = (
            db.query(Asset)
            .filter(
                and_(
                    Asset.id == array_id,
                    Asset.tenant_id == tenant_id,
                    Asset.component_type == "solar_array",
                )
            )
            .first()
        )

        if not array:
            return None, 0, 0, {}

        dynamic_attrs = array.dynamic_attributes or {}
        number_of_strings = dynamic_attrs.get("number_of_strings", 0)
        panels_per_string = dynamic_attrs.get("panels_per_string", 0)
        string_assignments = dynamic_attrs.get("string_assignments", {})

        return array, number_of_strings, panels_per_string, string_assignments

    @staticmethod
    def _parse_installation_date(date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse installation date from string

        Returns:
            datetime object or None
        """
        if not date_str:
            return None

        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None

    @staticmethod
    def _build_panel_data(
        row_data: Dict[str, Any], plant_id: int
    ) -> Dict[str, Any]:
        """
        Build panel data dictionary from row data

        Returns:
            Dictionary ready for Asset creation
        """
        installation_date = BulkImportService._parse_installation_date(
            row_data.get("installation_date")
        )

        return {
            "name": row_data["name"],
            "model": row_data.get("model"),
            "manufacturer": row_data.get("manufacturer"),
            "serial_number": row_data.get("serial_number"),
            "location": row_data.get("location"),
            "installation_date": installation_date,
            "status": row_data.get("status", "operational"),
            "component_type": "panel",
            "plant_id": plant_id,
            "dynamic_attributes": {
                "power_rating": (
                    float(row_data["power_rating"]) if row_data.get("power_rating") else None
                ),
                "efficiency": (
                    float(row_data["efficiency"]) if row_data.get("efficiency") else None
                ),
                "nominal_voltage": (
                    float(row_data["voltage"]) if row_data.get("voltage") else None
                ),
                "nominal_current": (
                    float(row_data["current"]) if row_data.get("current") else None
                ),
            },
        }

    @staticmethod
    def _check_duplicate_serial(
        db: Session, serial_number: str, tenant_id: str
    ) -> bool:
        """
        Check if serial number already exists

        Returns:
            True if duplicate found, False otherwise
        """
        if not serial_number:
            return False

        existing = (
            db.query(Asset)
            .filter(
                and_(
                    Asset.serial_number == serial_number,
                    Asset.tenant_id == tenant_id,
                )
            )
            .first()
        )
        return existing is not None

    @staticmethod
    def _create_panel_asset(
        db: Session, panel_data: Dict[str, Any], tenant_id: str, user_id: int
    ) -> Asset:
        """
        Create single panel asset

        Returns:
            Created Asset instance
        """
        panel = Asset(
            tenant_id=tenant_id,
            name=panel_data["name"],
            model=panel_data.get("model"),
            manufacturer=panel_data.get("manufacturer"),
            serial_number=panel_data.get("serial_number"),
            component_type="panel",
            plant_id=panel_data["plant_id"],
            location=panel_data.get("location"),
            installation_date=panel_data.get("installation_date"),
            status=panel_data.get("status", "operational"),
            dynamic_attributes=panel_data.get("dynamic_attributes", {}),
            created_by=user_id,
        )
        db.add(panel)
        db.flush()  # Get the ID
        return panel

    @staticmethod
    def _update_array_string_assignments(
        array: Asset, created_panels: List[Dict], panel_string_assignments: Dict[int, int]
    ) -> None:
        """
        Update array with string assignments for created panels
        """
        if not array or not panel_string_assignments:
            return

        dynamic_attrs = array.dynamic_attributes or {}
        string_assignments = dynamic_attrs.get("string_assignments", {})

        # Update string assignments
        for panel_info in created_panels:
            panel_id = panel_info["id"]
            string_num = panel_info.get("string_number")
            if string_num is not None:
                string_assignments[str(panel_id)] = string_num

        # Update attached panels list
        attached_panels = dynamic_attrs.get("attached_panels", [])
        for panel_info in created_panels:
            panel_id_str = str(panel_info["id"])
            if panel_id_str not in attached_panels:
                attached_panels.append(panel_id_str)

        dynamic_attrs["string_assignments"] = string_assignments
        dynamic_attrs["attached_panels"] = attached_panels
        array.dynamic_attributes = dynamic_attrs

    @staticmethod
    def import_panels_from_csv(
        db: Session,
        plant_id: int,
        array_id: int,
        csv_content: str,
        tenant_id: str,
        user_id: int,
        has_header: bool = True,
    ) -> Dict[str, Any]:
        """
        Import panels from CSV with string assignment

        REFACTORED: Extracted helper methods to reduce complexity
        Complexity reduced from 23 to ~8
        """
        import_results = {"success": 0, "failed": 0, "errors": [], "imported_panels": []}

        try:
            # Verify plant exists
            plant = BulkImportService._verify_plant(db, plant_id, tenant_id)

            # Load array configuration
            array, number_of_strings, panels_per_string, string_assignments = (
                BulkImportService._load_array_configuration(db, array_id, tenant_id)
            )

            # Parse CSV
            rows, parse_errors = BulkImportService.parse_csv(csv_content, has_header)
            import_results["errors"].extend(parse_errors)

            if parse_errors:
                import_results["failed"] = len(rows)
                return import_results

            # Prepare data structures
            created_panels = []
            panel_string_assignments = {}

            # Process each row
            for row_info in rows:
                row_data = row_info["data"]
                row_num = row_info["row_number"]

                # Validate row
                validation_errors = BulkImportService.validate_panel_row(
                    row_data, array_id, plant_id, db, tenant_id,
                    number_of_strings, panels_per_string
                )

                if validation_errors:
                    for error in validation_errors:
                        import_results["errors"].append(f"Row {row_num}: {error}")
                    import_results["failed"] += 1
                    continue

                # Build panel data
                panel_data = BulkImportService._build_panel_data(row_data, plant_id)

                # Check for duplicate serial number
                if BulkImportService._check_duplicate_serial(
                    db, panel_data.get("serial_number"), tenant_id
                ):
                    import_results["errors"].append(
                        f"Row {row_num}: Serial number {panel_data['serial_number']} already exists"
                    )
                    import_results["failed"] += 1
                    continue

                # Create panel
                try:
                    panel = BulkImportService._create_panel_asset(
                        db, panel_data, tenant_id, user_id
                    )

                    # Track string assignment
                    string_number = row_data.get("string_number")
                    created_panel_info = {
                        "id": panel.id,
                        "name": panel.name,
                        "string_number": int(string_number) if string_number else None,
                    }
                    created_panels.append(created_panel_info)

                except Exception as e:
                    import_results["errors"].append(f"Row {row_num}: Failed to create panel: {str(e)}")
                    import_results["failed"] += 1
                    logger.error(f"Error creating panel in row {row_num}: {e}")
                    continue

            # Update array string assignments
            BulkImportService._update_array_string_assignments(
                array, created_panels, panel_string_assignments
            )

            # Commit all changes
            db.commit()

            import_results["success"] = len(created_panels)
            import_results["imported_panels"] = created_panels

            logger.info(f"Imported {len(created_panels)} panels for plant {plant_id}")

        except Exception as e:
            db.rollback()
            logger.error(f"Error importing panels: {e}")
            import_results["errors"].append(f"Import failed: {str(e)}")

        return import_results

    @staticmethod
    def generate_csv_template() -> str:
        """Generate CSV template for panel import"""
        header = ",".join(BulkImportService.REQUIRED_COLUMNS + BulkImportService.OPTIONAL_COLUMNS)
        example_row = ",".join(
            [
                "Panel-001",  # name
                "JKM420M-72H-V",  # model
                "Jinko Solar",  # manufacturer
                "SN001234",  # serial_number
                "Row 1, Position 1",  # location
                "2024-01-15",  # installation_date
                "operational",  # status
                "420",  # power_rating (W)
                "21.5",  # efficiency (%)
                "41.0",  # voltage (V)
                "10.24",  # current (A)
                "1",  # string_number
                "Notes here",  # notes
            ]
        )
        return f"{header}\n{example_row}"
