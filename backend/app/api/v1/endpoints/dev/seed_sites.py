"""
Seed sites, storage units, and consumers for development testing
Split from monolithic dev.py for better maintainability
"""

from sqlalchemy.orm import Session
from typing import List

from app.models.site import Site, SiteTypeEnum, StorageUnit, Consumer


def seed_sites(db: Session) -> tuple[dict, List[Site]]:
    """
    Create test sites

    Returns:
        tuple: (results dict, list of created sites)
    """
    results = {"sites": []}

    sites_data = [
        {
            "name": "Solar Park North",
            "code": "SPN-001",
            "site_type": SiteTypeEnum.INDUSTRIAL,
            "status": "active",
            "location": "Northern Italy",
            "city": "Milan",
            "province": "MI",
            "region": "Lombardy",
            "country": "Italy",
            "latitude": 45.4642,
            "longitude": 9.1900,
            "capacity": 5000.0,
            "efficiency": 85.5,
        },
        {
            "name": "Wind Farm Central",
            "code": "WFC-001",
            "site_type": SiteTypeEnum.INDUSTRIAL,
            "status": "active",
            "location": "Central Italy",
            "city": "Rome",
            "province": "RM",
            "region": "Lazio",
            "country": "Italy",
            "latitude": 41.9028,
            "longitude": 12.4964,
            "capacity": 3000.0,
            "efficiency": 78.2,
        },
        {
            "name": "Solar Complex South",
            "code": "SCS-001",
            "site_type": SiteTypeEnum.COMMERCIAL,
            "status": "active",
            "location": "Southern Italy",
            "city": "Naples",
            "province": "NA",
            "region": "Campania",
            "country": "Italy",
            "latitude": 40.8518,
            "longitude": 14.2681,
            "capacity": 2500.0,
            "efficiency": 82.0,
        },
    ]

    created_sites = []
    for site_data in sites_data:
        existing_site = (
            db.query(Site)
            .filter(Site.tenant_id == "demo", Site.code == site_data["code"])
            .first()
        )

        if not existing_site:
            site = Site(tenant_id="demo", **site_data)
            db.add(site)
            db.flush()
            created_sites.append(site)
            results["sites"].append({"id": site.id, "name": site.name, "code": site.code})
        else:
            created_sites.append(existing_site)

    db.commit()
    return results, created_sites


def seed_storage_units(db: Session, sites: List[Site]) -> dict:
    """
    Create test storage units for sites

    Args:
        sites: List of sites to attach storage units to

    Returns:
        dict: Results with storage unit info
    """
    results = {"storage_units": []}

    if not sites or len(sites) < 2:
        return results

    storage_units_data = [
        {
            "site_id": sites[0].id,
            "name": "BESS Alpha",
            "code": "BESS-001",
            "capacity_kwh": 500.0,
            "rated_power_kw": 250.0,
            "chemistry_type": "Li-ion",
            "efficiency": 95.0,
            "status": "operational",
            "manufacturer": "Tesla",
            "model": "Megapack",
        },
        {
            "site_id": sites[1].id,
            "name": "BESS Beta",
            "code": "BESS-002",
            "capacity_kwh": 300.0,
            "rated_power_kw": 150.0,
            "chemistry_type": "Li-ion",
            "efficiency": 93.0,
            "status": "operational",
            "manufacturer": "BYD",
            "model": "Battery Box",
        },
    ]

    for su_data in storage_units_data:
        existing_su = (
            db.query(StorageUnit)
            .filter(StorageUnit.tenant_id == "demo", StorageUnit.code == su_data["code"])
            .first()
        )

        if not existing_su:
            storage_unit = StorageUnit(tenant_id="demo", **su_data)
            db.add(storage_unit)
            db.flush()
            results["storage_units"].append({"id": storage_unit.id, "name": storage_unit.name})

    db.commit()
    return results


def seed_consumers(db: Session, sites: List[Site]) -> dict:
    """
    Create test consumers for sites

    Args:
        sites: List of sites to attach consumers to

    Returns:
        dict: Results with consumer info
    """
    results = {"consumers": []}

    if not sites or len(sites) < 2:
        return results

    consumers_data = [
        {
            "site_id": sites[0].id,
            "name": "Industrial Consumer A",
            "code": "CONS-001",
            "consumer_type": "industrial",
            "average_consumption_kw": 150.0,
            "peak_consumption_kw": 250.0,
            "status": "active",
            "pod_id": "IT001E12345678",
        },
        {
            "site_id": sites[0].id,
            "name": "Commercial Consumer B",
            "code": "CONS-002",
            "consumer_type": "commercial",
            "average_consumption_kw": 50.0,
            "peak_consumption_kw": 100.0,
            "status": "active",
            "pod_id": "IT001E12345679",
        },
        {
            "site_id": sites[1].id,
            "name": "Residential Consumer C",
            "code": "CONS-003",
            "consumer_type": "residential",
            "average_consumption_kw": 5.0,
            "peak_consumption_kw": 10.0,
            "status": "active",
            "pod_id": "IT001E12345680",
        },
    ]

    for cons_data in consumers_data:
        existing_cons = (
            db.query(Consumer)
            .filter(Consumer.tenant_id == "demo", Consumer.code == cons_data["code"])
            .first()
        )

        if not existing_cons:
            consumer = Consumer(tenant_id="demo", **cons_data)
            db.add(consumer)
            db.flush()
            results["consumers"].append({"id": consumer.id, "name": consumer.name})

    db.commit()
    return results
