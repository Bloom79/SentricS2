"""
Seed CERs (Renewable Energy Communities) for development testing
Split from monolithic dev.py for better maintainability
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.models.user import User
from app.models.cer import CER, CERMember, CERLegalType, CERStatus, CERType
from app.core.geography import create_point, create_polygon


def seed_cers(db: Session, user: User, plants: List[dict]) -> tuple[dict, List[CER]]:
    """
    Create test CERs (Renewable Energy Communities)

    Args:
        user: User to set as creator
        plants: List of plant dicts (for later linking)

    Returns:
        tuple: (results dict, list of created CERs)
    """
    results = {"cers": []}

    if not plants:
        return results, []

    cers_data = [
        {
            "name": "Green Energy Community Milano",
            "description": "Renewable energy community in Northern Italy",
            "legal_type": CERLegalType.COOPERATIVE,
            "type": CERType.ACTIVE,
            "status": CERStatus.ACTIVE,
            "address": "Via Solare 1, Milan",
            "region": "Lombardy",
            "province": "MI",
            "municipality": "Milan",
            "primary_substation_id": "PS-MIL-001",
            "location": [9.1900, 45.4642],  # [lon, lat]
            "boundary": [
                [9.18, 45.45],
                [9.20, 45.45],
                [9.20, 45.48],
                [9.18, 45.48],
                [9.18, 45.45],
            ],
            "technical_info": {"total_capacity_kw": 4300.0},
            "billing_settings": {"tariff_type": "standard"},
        },
        {
            "name": "Solar Community Lazio",
            "description": "Community energy project in Central Italy",
            "legal_type": CERLegalType.ASSOCIATION,
            "type": CERType.ACTIVE,
            "status": CERStatus.ACTIVE,
            "address": "Via Vento 10, Rome",
            "region": "Lazio",
            "province": "RM",
            "municipality": "Rome",
            "primary_substation_id": "PS-ROM-001",
            "location": [12.4964, 41.9028],
            "boundary": [
                [12.48, 41.89],
                [12.51, 41.89],
                [12.51, 41.92],
                [12.48, 41.92],
                [12.48, 41.89],
            ],
            "technical_info": {"total_capacity_kw": 8000.0},
            "billing_settings": {"tariff_type": "premium"},
        },
        {
            "name": "Campania Energy Cooperative",
            "description": "Southern Italy renewable energy cooperative",
            "legal_type": CERLegalType.COOPERATIVE,
            "type": CERType.ACTIVE,
            "status": CERStatus.PENDING,
            "address": "Via Sole 5, Naples",
            "region": "Campania",
            "province": "NA",
            "municipality": "Naples",
            "primary_substation_id": "PS-NAP-001",
            "location": [14.2681, 40.8518],
            "boundary": [
                [14.26, 40.84],
                [14.28, 40.84],
                [14.28, 40.86],
                [14.26, 40.86],
                [14.26, 40.84],
            ],
            "technical_info": {"total_capacity_kw": 2000.0},
            "billing_settings": {"tariff_type": "standard"},
        },
    ]

    created_cers = []
    for cer_data in cers_data:
        existing_cer = (
            db.query(CER).filter(CER.tenant_id == "demo", CER.name == cer_data["name"]).first()
        )

        if not existing_cer:
            # Create location point
            location_wkt = None
            if cer_data.get("location"):
                location_wkt = create_point(cer_data["location"][0], cer_data["location"][1])

            # Create boundary polygon
            boundary_wkt = None
            if cer_data.get("boundary"):
                boundary_wkt = create_polygon(cer_data["boundary"])

            cer = CER(
                tenant_id="demo",
                created_by=user.id,
                name=cer_data["name"],
                description=cer_data["description"],
                legal_type=cer_data["legal_type"],
                type=cer_data["type"],
                status=cer_data["status"],
                address=cer_data["address"],
                region=cer_data["region"],
                province=cer_data["province"],
                municipality=cer_data["municipality"],
                primary_substation_id=cer_data["primary_substation_id"],
                location=location_wkt,
                boundary=boundary_wkt,
                technical_info=cer_data.get("technical_info", {}),
                billing_settings=cer_data.get("billing_settings", {}),
                total_capacity=cer_data.get("technical_info", {}).get("total_capacity_kw", 0.0),
            )
            db.add(cer)
            db.flush()
            created_cers.append(cer)
            results["cers"].append({"id": cer.id, "name": cer.name})
        else:
            created_cers.append(existing_cer)

    db.commit()
    return results, created_cers


def link_plants_to_cers(db: Session, cers: List[CER], plants: List[dict]) -> None:
    """
    Link plants to CERs

    Args:
        cers: List of CERs
        plants: List of plant dicts with id
    """
    if not cers or not plants:
        return

    # Link first 2 plants to first CER
    for i, plant_info in enumerate(plants[:2]):
        if i < len(cers):
            db.execute(
                text("UPDATE plants SET cer_id = :cer_id WHERE id = :plant_id"),
                {"cer_id": cers[0].id, "plant_id": plant_info["id"]},
            )

    # Link next 2 plants to second CER
    for i, plant_info in enumerate(plants[2:4]):
        if i < len(cers):
            db.execute(
                text("UPDATE plants SET cer_id = :cer_id WHERE id = :plant_id"),
                {"cer_id": cers[1].id, "plant_id": plant_info["id"]},
            )

    db.commit()


def seed_cer_members(db: Session, user: User, cers: List[CER]) -> dict:
    """
    Create test CER members

    Args:
        user: User to set as creator
        cers: List of CERs to create members for

    Returns:
        dict: Results with member info
    """
    results = {"cer_members": []}

    if not cers or len(cers) < 3:
        return results

    members_data = [
        {
            "cer_id": cers[0].id,
            "name": "Consumer Member A",
            "address": "Via Milano 1, Milan",
            "member_type": "consumer",
            "pod_id": "IT001E12345681",
            "load_profile_type": "residential",
            "contracted_power": 3.0,
            "status": "active",
        },
        {
            "cer_id": cers[0].id,
            "name": "Producer Member B",
            "address": "Via Milano 2, Milan",
            "member_type": "producer",
            "pod_id": "IT001E12345682",
            "load_profile_type": "commercial",
            "contracted_power": 5.0,
            "status": "active",
        },
        {
            "cer_id": cers[0].id,
            "name": "Prosumer Member C",
            "address": "Via Milano 3, Milan",
            "member_type": "prosumer",
            "pod_id": "IT001E12345683",
            "load_profile_type": "residential",
            "contracted_power": 4.5,
            "status": "active",
        },
        {
            "cer_id": cers[1].id,
            "name": "Consumer Member D",
            "address": "Via Roma 1, Rome",
            "member_type": "consumer",
            "pod_id": "IT001E12345684",
            "load_profile_type": "residential",
            "contracted_power": 2.5,
            "status": "active",
        },
        {
            "cer_id": cers[1].id,
            "name": "Producer Member E",
            "address": "Via Roma 2, Rome",
            "member_type": "producer",
            "pod_id": "IT001E12345685",
            "load_profile_type": "industrial",
            "contracted_power": 10.0,
            "status": "active",
        },
        {
            "cer_id": cers[2].id,
            "name": "Consumer Member F",
            "address": "Via Napoli 1, Naples",
            "member_type": "consumer",
            "pod_id": "IT001E12345686",
            "load_profile_type": "residential",
            "contracted_power": 2.0,
            "status": "active",
        },
    ]

    for member_data in members_data:
        existing_member = (
            db.query(CERMember)
            .filter(CERMember.tenant_id == "demo", CERMember.pod_id == member_data["pod_id"])
            .first()
        )

        if not existing_member:
            member = CERMember(tenant_id="demo", created_by=user.id, **member_data)
            db.add(member)
            db.flush()
            results["cer_members"].append(
                {"id": member.id, "name": member.name, "cer_id": member.cer_id}
            )

    db.commit()
    return results


def update_cer_capacities(db: Session, cers: List[CER]) -> None:
    """
    Update CER total capacity from linked plants

    Args:
        cers: List of CERs to update
    """
    for cer in cers:
        total_capacity = (
            db.execute(
                text(
                    "SELECT COALESCE(SUM(power_kw), 0) FROM plants WHERE cer_id = :cer_id AND deleted_at IS NULL"
                ),
                {"cer_id": cer.id},
            ).scalar()
            or 0.0
        )

        cer.total_capacity = total_capacity

    db.commit()
