"""
Unit tests for Plant API endpoints

Tests all plant-related API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.plant import Plant
from app.models.user import User


class TestPlantEndpoints:
    """Test suite for Plant API endpoints"""

    def test_create_plant_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_tenant
    ):
        """Test POST /api/v1/plants - successful plant creation"""
        # Arrange
        plant_data = {
            "name": "API Test Plant",
            "code": "API-TEST-001",
            "power": "100 kW",
            "power_kw": 100.0,
            "status": "IN_OPERATION",
            "type": "PHOTOVOLTAIC",
            "location": "Rome, Italy"
        }

        # Act
        response = client.post(
            "/api/v1/plants",
            json=plant_data,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "API Test Plant"
        assert data["code"] == "API-TEST-001"
        assert data["power_kw"] == 100.0
        assert "id" in data

    def test_create_plant_unauthorized(
        self,
        client: TestClient
    ):
        """Test POST /api/v1/plants - without authentication"""
        # Arrange
        plant_data = {
            "name": "Test Plant",
            "code": "TEST-001",
            "power_kw": 100.0,
            "status": "IN_OPERATION",
            "type": "PHOTOVOLTAIC"
        }

        # Act
        response = client.post("/api/v1/plants", json=plant_data)

        # Assert
        assert response.status_code == 401

    def test_get_plant_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plant: Plant
    ):
        """Test GET /api/v1/plants/{id} - successful retrieval"""
        # Act
        response = client.get(
            f"/api/v1/plants/{test_plant.id}",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_plant.id
        assert data["name"] == test_plant.name
        assert data["code"] == test_plant.code

    def test_get_plant_not_found(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test GET /api/v1/plants/{id} - plant not found"""
        # Act
        response = client.get(
            "/api/v1/plants/99999",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 404

    def test_list_plants_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plant: Plant
    ):
        """Test GET /api/v1/plants - list all plants"""
        # Act
        response = client.get(
            "/api/v1/plants",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_plants_filter_by_type(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plant: Plant
    ):
        """Test GET /api/v1/plants?type=PHOTOVOLTAIC - filter by type"""
        # Act
        response = client.get(
            "/api/v1/plants?type=PHOTOVOLTAIC",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert all(p["type"] == "PHOTOVOLTAIC" for p in data)

    def test_update_plant_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plant: Plant
    ):
        """Test PUT /api/v1/plants/{id} - successful update"""
        # Arrange
        update_data = {
            "name": "Updated Plant Name",
            "power_kw": 200.0
        }

        # Act
        response = client.put(
            f"/api/v1/plants/{test_plant.id}",
            json=update_data,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Plant Name"
        assert data["power_kw"] == 200.0

    def test_delete_plant_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plant: Plant
    ):
        """Test DELETE /api/v1/plants/{id} - successful deletion"""
        # Act
        response = client.delete(
            f"/api/v1/plants/{test_plant.id}",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 204

    def test_get_plant_stats_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plant: Plant
    ):
        """Test GET /api/v1/plants/{id}/stats - get plant statistics"""
        # Act
        response = client.get(
            f"/api/v1/plants/{test_plant.id}/stats",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "plant_id" in data
        assert "total_assets" in data
        assert "operational_assets" in data
        assert "total_capacity_kw" in data

    def test_create_plant_validation_error(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test POST /api/v1/plants - with invalid data"""
        # Arrange - Missing required fields
        plant_data = {
            "name": "Invalid Plant"
            # Missing required fields
        }

        # Act
        response = client.post(
            "/api/v1/plants",
            json=plant_data,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 422  # Validation error
