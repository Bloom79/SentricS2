"""
Bulk Import Service for Assets (especially panels)
Handles CSV parsing, validation, and batch creation
"""

from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import csv
import io
import logging

from app.models.asset import Asset
from app.models.plant import Plant

logger = logging.getLogger(__name__)


class BulkImportService:
    """Service for bulk importing assets from CSV"""

    REQUIRED_COLUMNS = ["name", "model"]
    OPTIONAL_COLUMNS = [
        "manufacturer", "serial_number", "location", "installation_date",
        "status", "power_rating", "efficiency", "voltage", "current",
        "string_number", "notes"
    ]

    @staticmethod
    def parse_csv(
        csv_content: str,
        has_header: bool = True
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Parse CSV content and return rows with errors"""
        errors = []
        rows = []

        try:
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            # Check required columns
            if has_header:
                reader_fieldnames = csv_reader.fieldnames or []
                missing_columns = [col for col in BulkImportService.REQUIRED_COLUMNS if col not in reader_fieldnames]
                if missing_columns:
                    errors.append(f"Missing required columns: {', '.join(missing_columns)}")
                    return rows, errors

            for row_num, row in enumerate(csv_reader, start=2 if has_header else 1):
                # Normalize keys (lowercase, strip spaces)
                normalized_row = {k.lower().strip(): v.strip() if v else None for k, v in row.items()}
                
                # Validate required fields
                row_errors = []
                for col in BulkImportService.REQUIRED_COLUMNS:
                    if not normalized_row.get(col):
                        row_errors.append(f"Row {row_num}: Missing required field '{col}'")
                
                if row_errors:
                    errors.extend(row_errors)
                    continue

                rows.append({
                    "row_number": row_num,
                    "data": normalized_row
                })

        except Exception as e:
            errors.append(f"CSV parsing error: {str(e)}")

        return rows, errors

    @staticmethod
    def validate_panel_row(
        row_data: Dict[str, Any],
        array_id: int,
        plant_id: int,
        db: Session,
        tenant_id: str,
        number_of_strings: int = 0,
        panels_per_string: int = 0
    ) -> List[str]:
        """Validate a single panel row"""
        errors = []

        # Validate string_number if provided
        string_number = row_data.get("string_number")
        if string_number:
            try:
                string_num = int(string_number)
                if string_num < 1:
                    errors.append("String number must be >= 1")
                elif number_of_strings > 0 and string_num > number_of_strings:
                    errors.append(f"String number must be <= {number_of_strings}")
            except ValueError:
                errors.append("String number must be a valid integer")

        # Validate date format
        installation_date = row_data.get("installation_date")
        if installation_date:
            try:
                datetime.strptime(installation_date, "%Y-%m-%d")
            except ValueError:
                try:
                    datetime.strptime(installation_date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    errors.append("Installation date must be in format YYYY-MM-DD or YYYY-MM-DD HH:MM:SS")

        # Validate status
        status = row_data.get("status", "operational")
        valid_statuses = ["operational", "maintenance", "offline", "decommissioned"]
        if status not in valid_statuses:
            errors.append(f"Status must be one of: {', '.join(valid_statuses)}")

        # Validate numeric fields
        numeric_fields = ["power_rating", "efficiency", "voltage", "current"]
        for field in numeric_fields:
            value = row_data.get(field)
            if value:
                try:
                    float(value)
                except ValueError:
                    errors.append(f"{field} must be a valid number")

        return errors

    @staticmethod
    def import_panels_from_csv(
        db: Session,
        plant_id: int,
        array_id: int,
        csv_content: str,
        tenant_id: str,
        user_id: int,
        has_header: bool = True
    ) -> Dict[str, Any]:
        """Import panels from CSV with string assignment"""
        import_results = {
            "success": 0,
            "failed": 0,
            "errors": [],
            "imported_panels": []
        }

        try:
            # Verify plant exists
            plant = db.query(Plant).filter(
                and_(
                    Plant.id == plant_id,
                    Plant.tenant_id == tenant_id
                )
            ).first()

            if not plant:
                raise ValueError(f"Plant {plant_id} not found")

            # Get array and string config if array_id provided
            array = None
            number_of_strings = 0
            panels_per_string = 0
            string_assignments = {}

            if array_id:
                array = db.query(Asset).filter(
                    and_(
                        Asset.id == array_id,
                        Asset.tenant_id == tenant_id,
                        Asset.component_type == "solar_array"
                    )
                ).first()

                if array:
                    dynamic_attrs = array.dynamic_attributes or {}
                    number_of_strings = dynamic_attrs.get("number_of_strings", 0)
                    panels_per_string = dynamic_attrs.get("panels_per_string", 0)
                    string_assignments = dynamic_attrs.get("string_assignments", {})

            # Parse CSV
            rows, parse_errors = BulkImportService.parse_csv(csv_content, has_header)
            import_results["errors"].extend(parse_errors)

            if parse_errors:
                import_results["failed"] = len(rows)
                return import_results

            # Validate and import each row
            panels_to_create = []
            panel_string_assignments = {}

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

                # Parse installation date
                installation_date = None
                if row_data.get("installation_date"):
                    try:
                        installation_date = datetime.strptime(row_data["installation_date"], "%Y-%m-%d")
                    except ValueError:
                        installation_date = datetime.strptime(row_data["installation_date"], "%Y-%m-%d %H:%M:%S")

                # Create panel asset data
                panel_data = {
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
                        "power_rating": float(row_data["power_rating"]) if row_data.get("power_rating") else None,
                        "efficiency": float(row_data["efficiency"]) if row_data.get("efficiency") else None,
                        "nominal_voltage": float(row_data["voltage"]) if row_data.get("voltage") else None,
                        "nominal_current": float(row_data["current"]) if row_data.get("current") else None,
                    }
                }

                panels_to_create.append({
                    **panel_data,
                    "row_number": row_num,  # Keep row number for error reporting
                })

                # Store string assignment if provided
                string_number = row_data.get("string_number")
                if string_number and array_id:
                    panel_string_assignments[len(panels_to_create) - 1] = int(string_number)

            # Batch create panels
            created_panels = []
            for idx, panel_data in enumerate(panels_to_create):
                try:
                    # Check for duplicate serial numbers
                    if panel_data.get("serial_number"):
                        existing = db.query(Asset).filter(
                            and_(
                                Asset.serial_number == panel_data["serial_number"],
                                Asset.tenant_id == tenant_id
                            )
                        ).first()
                        if existing:
                            import_results["errors"].append(
                                f"Row {panel_data.get('row_number', idx + 1)}: Serial number {panel_data['serial_number']} already exists"
                            )
                            import_results["failed"] += 1
                            continue

                    # Create asset
                    panel = Asset(
                        tenant_id=tenant_id,
                        name=panel_data["name"],
                        model=panel_data.get("model"),
                        manufacturer=panel_data.get("manufacturer"),
                        serial_number=panel_data.get("serial_number"),
                        component_type="panel",
                        plant_id=plant_id,
                        location=panel_data.get("location"),
                        installation_date=panel_data.get("installation_date"),
                        status=panel_data.get("status", "operational"),
                        dynamic_attributes=panel_data.get("dynamic_attributes", {}),
                        created_by=user_id
                    )

                    db.add(panel)
                    db.flush()  # Get the ID

                    created_panels.append({
                        "id": panel.id,
                        "name": panel.name,
                        "string_number": panel_string_assignments.get(idx)
                    })

                    # Assign to string if specified
                    if idx in panel_string_assignments and array:
                        string_num = panel_string_assignments[idx]
                        string_assignments[str(panel.id)] = string_num

                except Exception as e:
                    import_results["errors"].append(
                        f"Row {panel_data.get('row_number', idx + 1)}: Failed to create panel: {str(e)}"
                    )
                    import_results["failed"] += 1
                    logger.error(f"Error creating panel in row {panel_data.get('row_number', idx + 1)}: {e}")
                    continue

            # Update array string assignments if panels were assigned
            if array and panel_string_assignments:
                dynamic_attrs = array.dynamic_attributes or {}
                dynamic_attrs["string_assignments"] = string_assignments
                attached_panels = dynamic_attrs.get("attached_panels", [])
                for panel_info in created_panels:
                    if str(panel_info["id"]) not in attached_panels:
                        attached_panels.append(str(panel_info["id"]))
                dynamic_attrs["attached_panels"] = attached_panels
                array.dynamic_attributes = dynamic_attrs

            db.commit()

            import_results["success"] = len(created_panels)
            import_results["imported_panels"] = created_panels

            logger.info(f"Imported {len(created_panels)} panels for plant {plant_id}")

        except Exception as e:
            db.rollback()
            logger.error(f"Error importing panels: {e}")
            import_results["errors"].append(f"Import failed: {str(e)}")
            import_results["failed"] = len(panels_to_create)

        return import_results

    @staticmethod
    def generate_csv_template() -> str:
        """Generate CSV template for panel import"""
        header = ",".join(BulkImportService.REQUIRED_COLUMNS + BulkImportService.OPTIONAL_COLUMNS)
        example_row = ",".join([
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
            "Initial installation"  # notes
        ])
        return f"{header}\n{example_row}"

