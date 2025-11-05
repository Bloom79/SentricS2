"""
Asset helper functions
Split from monolithic assets.py for better maintainability
"""

from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


def parse_dynamic_attributes(value: Any) -> Dict[str, Any]:
    """Parse dynamic_attributes from JSON string or dict to dict"""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value) if value else {}
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Failed to parse dynamic_attributes as JSON: {value}")
            return {}
    return {}
