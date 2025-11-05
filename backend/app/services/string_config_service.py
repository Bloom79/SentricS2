"""
String Configuration Service for Solar Arrays
Manages string assignments and configuration for solar arrays
REFACTORED: Reduced complexity by extracting helper methods
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

from app.models.asset import Asset
from app.services.base import BaseService

logger = logging.getLogger(__name__)


class StringConfigService(BaseService):
    """Service for managing string configurations"""

    @staticmethod
    def get_string_config(db: Session, array_id: int, tenant_id: str) -> Dict[str, Any]:
        """Get string configuration for a solar array"""
        try:
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
                raise ValueError(f"Solar array {array_id} not found")

            dynamic_attrs = array.dynamic_attributes or {}

            return {
                "array_id": array_id,
                "array_name": array.name,
                "number_of_strings": dynamic_attrs.get("number_of_strings", 0),
                "panels_per_string": dynamic_attrs.get("panels_per_string", 0),
                "string_assignments": dynamic_attrs.get("string_assignments", {}),
                "attached_panels": dynamic_attrs.get("attached_panels", []),
            }

        except Exception as e:
            logger.error(f"Error getting string config for array {array_id}: {e}")
            raise

    @staticmethod
    def update_string_config(
        db: Session, array_id: int, number_of_strings: int, panels_per_string: int, tenant_id: str
    ) -> Asset:
        """Update string configuration (number of strings, panels per string)"""
        try:
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
                raise ValueError(f"Solar array {array_id} not found")

            dynamic_attrs = array.dynamic_attributes or {}
            dynamic_attrs["number_of_strings"] = number_of_strings
            dynamic_attrs["panels_per_string"] = panels_per_string

            # Initialize string_assignments if not exists
            if "string_assignments" not in dynamic_attrs:
                dynamic_attrs["string_assignments"] = {}

            array.dynamic_attributes = dynamic_attrs
            db.commit()
            db.refresh(array)

            logger.info(f"Updated string config for array {array_id}")
            return array

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating string config for array {array_id}: {e}")
            raise

    @staticmethod
    def _get_array(db: Session, array_id: int, tenant_id: str) -> Asset:
        """
        Get solar array by ID with validation

        Raises:
            ValueError if array not found
        """
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
            raise ValueError(f"Solar array {array_id} not found")

        return array

    @staticmethod
    def _validate_string_number(string_number: int, number_of_strings: int) -> None:
        """
        Validate string number is within range

        Raises:
            ValueError if string number is invalid
        """
        if string_number < 1 or string_number > number_of_strings:
            raise ValueError(f"String number must be between 1 and {number_of_strings}")

    @staticmethod
    def _validate_panel_count(panel_ids: List[int], panels_per_string: int) -> None:
        """
        Validate panel count doesn't exceed maximum

        Raises:
            ValueError if too many panels
        """
        if len(panel_ids) > panels_per_string:
            raise ValueError(f"Maximum {panels_per_string} panels per string")

    @staticmethod
    def _verify_panels_exist(
        db: Session, panel_ids: List[int], tenant_id: str, plant_id: int
    ) -> List[Asset]:
        """
        Verify all panels exist and belong to the same plant

        Raises:
            ValueError if panels not found or don't belong to plant
        """
        panels = (
            db.query(Asset)
            .filter(
                and_(
                    Asset.id.in_(panel_ids),
                    Asset.tenant_id == tenant_id,
                    Asset.component_type == "panel",
                    Asset.plant_id == plant_id,
                )
            )
            .all()
        )

        if len(panels) != len(panel_ids):
            raise ValueError("Some panels not found or do not belong to this plant")

        return panels

    @staticmethod
    def _remove_panels_from_other_strings(
        string_assignments: Dict[str, int], string_number: int, panel_ids: List[int]
    ) -> None:
        """
        Remove panels from the current string if they're not in the new panel list

        Modifies string_assignments in place
        """
        panel_id_strs = [str(p) for p in panel_ids]
        for panel_id_str, assigned_string in list(string_assignments.items()):
            if assigned_string == string_number and panel_id_str not in panel_id_strs:
                del string_assignments[panel_id_str]

    @staticmethod
    def _update_attached_panels(
        attached_panels: List[str], panel_ids: List[int]
    ) -> List[str]:
        """
        Add panels to attached_panels list if not already present

        Returns:
            Updated attached_panels list
        """
        for panel_id in panel_ids:
            if str(panel_id) not in attached_panels:
                attached_panels.append(str(panel_id))
        return attached_panels

    @staticmethod
    def assign_panels_to_string(
        db: Session, array_id: int, string_number: int, panel_ids: List[int], tenant_id: str
    ) -> Asset:
        """
        Assign panels to a specific string

        REFACTORED: Complexity reduced from 12 to ~5 by extracting helpers
        """
        try:
            # Get array
            array = StringConfigService._get_array(db, array_id, tenant_id)

            # Load configuration
            dynamic_attrs = array.dynamic_attributes or {}
            panels_per_string = dynamic_attrs.get("panels_per_string", 0)
            number_of_strings = dynamic_attrs.get("number_of_strings", 0)

            # Validate inputs
            StringConfigService._validate_string_number(string_number, number_of_strings)
            StringConfigService._validate_panel_count(panel_ids, panels_per_string)

            # Verify panels exist and belong to plant
            StringConfigService._verify_panels_exist(db, panel_ids, tenant_id, array.plant_id)

            # Get current string assignments
            string_assignments = dynamic_attrs.get("string_assignments", {})

            # Remove panels from this string if not in new list
            StringConfigService._remove_panels_from_other_strings(
                string_assignments, string_number, panel_ids
            )

            # Assign panels to string
            for panel_id in panel_ids:
                string_assignments[str(panel_id)] = string_number

            dynamic_attrs["string_assignments"] = string_assignments

            # Update attached_panels list
            attached_panels = dynamic_attrs.get("attached_panels", [])
            dynamic_attrs["attached_panels"] = StringConfigService._update_attached_panels(
                attached_panels, panel_ids
            )

            # Save changes
            array.dynamic_attributes = dynamic_attrs
            db.commit()
            db.refresh(array)

            logger.info(
                f"Assigned {len(panel_ids)} panels to string {string_number} in array {array_id}"
            )
            return array

        except Exception as e:
            db.rollback()
            logger.error(f"Error assigning panels to string: {e}")
            raise

    @staticmethod
    def remove_panel_from_string(
        db: Session, array_id: int, panel_id: int, tenant_id: str
    ) -> Asset:
        """Remove a panel from its assigned string"""
        try:
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
                raise ValueError(f"Solar array {array_id} not found")

            dynamic_attrs = array.dynamic_attributes or {}
            string_assignments = dynamic_attrs.get("string_assignments", {})

            # Remove panel assignment
            if str(panel_id) in string_assignments:
                del string_assignments[str(panel_id)]

            # Remove from attached_panels
            attached_panels = dynamic_attrs.get("attached_panels", [])
            if str(panel_id) in attached_panels:
                attached_panels.remove(str(panel_id))

            dynamic_attrs["string_assignments"] = string_assignments
            dynamic_attrs["attached_panels"] = attached_panels

            array.dynamic_attributes = dynamic_attrs
            db.commit()
            db.refresh(array)

            logger.info(f"Removed panel {panel_id} from string in array {array_id}")
            return array

        except Exception as e:
            db.rollback()
            logger.error(f"Error removing panel from string: {e}")
            raise

    @staticmethod
    def get_string_details(
        db: Session, array_id: int, string_number: int, tenant_id: str
    ) -> Dict[str, Any]:
        """Get details for a specific string including panel list and metrics"""
        try:
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
                raise ValueError(f"Solar array {array_id} not found")

            dynamic_attrs = array.dynamic_attributes or {}
            string_assignments = dynamic_attrs.get("string_assignments", {})
            panels_per_string = dynamic_attrs.get("panels_per_string", 0)

            # Get panels assigned to this string
            assigned_panel_ids = [
                int(panel_id)
                for panel_id, str_num in string_assignments.items()
                if str_num == string_number
            ]

            # Fetch panel details
            panels = (
                db.query(Asset)
                .filter(and_(Asset.id.in_(assigned_panel_ids), Asset.tenant_id == tenant_id))
                .all()
            )

            # Calculate string metrics
            total_voltage = sum(
                (p.dynamic_attributes or {}).get("nominal_voltage", 0) or 0 for p in panels
            )
            nominal_current = (
                panels[0].dynamic_attributes.get("nominal_current", 0) if panels else 0
            )
            total_power = total_voltage * nominal_current if nominal_current else 0

            return {
                "string_number": string_number,
                "array_id": array_id,
                "array_name": array.name,
                "panels": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "model": p.model,
                        "voltage": (p.dynamic_attributes or {}).get("nominal_voltage", 0),
                        "current": (p.dynamic_attributes or {}).get("nominal_current", 0),
                        "power": (p.dynamic_attributes or {}).get("power_rating", 0),
                    }
                    for p in panels
                ],
                "panels_count": len(panels),
                "max_panels": panels_per_string,
                "status": (
                    "full"
                    if len(panels) == panels_per_string
                    else ("partial" if len(panels) > 0 else "empty")
                ),
                "total_voltage": total_voltage,
                "nominal_current": nominal_current,
                "total_power": total_power,
            }

        except Exception as e:
            logger.error(f"Error getting string details: {e}")
            raise

    @staticmethod
    def get_all_strings(db: Session, array_id: int, tenant_id: str) -> List[Dict[str, Any]]:
        """Get all strings for an array with their status"""
        try:
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
                raise ValueError(f"Solar array {array_id} not found")

            dynamic_attrs = array.dynamic_attributes or {}
            number_of_strings = dynamic_attrs.get("number_of_strings", 0)
            panels_per_string = dynamic_attrs.get("panels_per_string", 0)
            string_assignments = dynamic_attrs.get("string_assignments", {})

            strings = []
            for string_num in range(1, number_of_strings + 1):
                assigned_panel_ids = [
                    int(panel_id)
                    for panel_id, str_num in string_assignments.items()
                    if str_num == string_num
                ]
                strings.append(
                    {
                        "string_number": string_num,
                        "string_code": f"STR{string_num:03d}",
                        "panels_count": len(assigned_panel_ids),
                        "max_panels": panels_per_string,
                        "status": (
                            "full"
                            if len(assigned_panel_ids) == panels_per_string
                            else ("partial" if len(assigned_panel_ids) > 0 else "empty")
                        ),
                    }
                )

            return strings

        except Exception as e:
            logger.error(f"Error getting all strings for array {array_id}: {e}")
            raise
