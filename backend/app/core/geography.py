"""
PostGIS geographic utilities
Migrated from Sentrics
"""

from typing import List, Tuple, Optional
from shapely.geometry import Point, Polygon
from shapely import wkt
import logging

logger = logging.getLogger(__name__)


def create_point(longitude: float, latitude: float) -> str:
    """
    Create PostGIS POINT from coordinates

    Args:
        longitude: Longitude (X coordinate)
        latitude: Latitude (Y coordinate)

    Returns:
        WKT string for PostGIS POINT
    """
    return f"POINT({longitude} {latitude})"


def create_polygon(coordinates: List[Tuple[float, float]]) -> str:
    """
    Create PostGIS POLYGON from coordinate list

    Args:
        coordinates: List of (longitude, latitude) tuples
                    Must form a closed polygon (first point = last point)

    Returns:
        WKT string for PostGIS POLYGON
    """
    if len(coordinates) < 4:
        raise ValueError("Polygon must have at least 4 points (including closing point)")

    # Ensure polygon is closed
    if coordinates[0] != coordinates[-1]:
        coordinates.append(coordinates[0])

    coords_str = ", ".join([f"{lon} {lat}" for lon, lat in coordinates])
    return f"POLYGON(({coords_str}))"


def validate_boundary(coordinates: List[Tuple[float, float]]) -> bool:
    """
    Validate boundary coordinates

    Args:
        coordinates: List of (longitude, latitude) tuples

    Returns:
        True if valid, False otherwise
    """
    if len(coordinates) < 4:
        return False

    # Check if coordinates form a valid polygon
    try:
        # Ensure closed
        if coordinates[0] != coordinates[-1]:
            coords = coordinates + [coordinates[0]]
        else:
            coords = coordinates

        polygon = Polygon(coords)
        return polygon.is_valid
    except Exception as e:
        logger.error(f"Boundary validation error: {e}")
        return False


def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate distance between two points in meters

    Args:
        point1: (longitude, latitude) tuple
        point2: (longitude, latitude) tuple

    Returns:
        Distance in meters
    """
    # Use PostGIS ST_Distance
    # Note: This would need a database session to execute
    # Example implementation:
    # from sqlalchemy import select
    # p1_wkt = create_point(point1[0], point1[1])
    # p2_wkt = create_point(point2[0], point2[1])
    # query = select([func.ST_Distance(func.ST_GeomFromText(p1_wkt, 4326), func.ST_GeomFromText(p2_wkt, 4326))])
    # result = db.execute(query).scalar()
    # In practice, use in a service method with db session
    return None  # Placeholder - implement with db session


def check_point_in_polygon(point: Tuple[float, float], polygon_wkt: str) -> bool:
    """
    Check if point is within polygon

    Args:
        point: (longitude, latitude) tuple
        polygon_wkt: WKT string of polygon

    Returns:
        True if point is within polygon
    """
    try:
        point_geom = Point(point[0], point[1])
        polygon_geom = wkt.loads(polygon_wkt)
        return polygon_geom.contains(point_geom)
    except Exception as e:
        logger.error(f"Point in polygon check error: {e}")
        return False


def get_boundary_area(polygon_wkt: str) -> Optional[float]:
    """
    Calculate area of polygon in square meters

    Args:
        polygon_wkt: WKT string of polygon

    Returns:
        Area in square meters, or None if error
    """
    try:
        polygon = wkt.loads(polygon_wkt)
        # Area in square degrees - convert to square meters (approximate)
        # For accurate conversion, use PostGIS ST_Area with proper SRID
        return polygon.area * 111000 * 111000  # Rough conversion
    except Exception as e:
        logger.error(f"Area calculation error: {e}")
        return None
