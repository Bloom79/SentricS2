#!/usr/bin/env python3
"""
Comprehensive CER Seed Data Script
Creates seed data covering all CER functionalities:
- CERs (Communities)
- CER Members (consumers, producers, prosumers)
- CER Member Assets
- Plants linked to CERs
- Participation Requests
- Compliance Requirements and Records (CER + Plant)
- Documents
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.cer import (
    CER, CERMember, CERParticipationRequest,
    CERLegalType, CERStatus, CERType, ParticipationRequestStatus
)
from app.models.cer_member_asset import CERMemberAsset, CERMemberAssetType, CERMemberAssetStatus
from app.models.plant import Plant, PlantStatusEnum, PlantTypeEnum
from app.models.compliance import (
    ComplianceRequirement, ComplianceRecord,
    ComplianceTypeEnum, ComplianceStatusEnum
)
from app.models.document import Document, DocumentTypeEnum, DocumentStatusEnum
from app.models.user import User
from app.models.tenant import Tenant
from datetime import datetime, timedelta, timezone
import json

def seed_cer_data(db: Session, tenant_id: str = "demo", user_id: int = 1):
    """Create comprehensive CER seed data"""
    
    print("🌱 Seeding CER data...")
    
    # Get or create user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print(f"⚠️  User {user_id} not found. Creating CER data will use user_id={user_id}")
    
    # 1. Create CERs
    print("\n📋 Creating CERs...")
    cer_data = [
        {
            "name": "Solar Community Milan",
            "description": "A cooperative renewable energy community in Milan focusing on solar energy sharing",
            "legal_type": CERLegalType.COOPERATIVE,
            "type": CERType.ACTIVE,
            "status": CERStatus.ACTIVE,
            "address": "Via Solferino 23, 20121 Milano, MI",
            "region": "Lombardy",
            "province": "MI",
            "municipality": "Milano",
            "primary_substation_id": "SUB-MI-001",
            "total_capacity": 250.0,
            "energy_source": "solar",
            "pnrr_funding_applied": True,
            "pnrr_funding_amount": 50000.0,
            "pnrr_funding_status": "approved",
            "gse_compliance_status": "compliant",
            "technical_info": {
                "max_members": 100,
                "sharing_model": "autoconsumo_diffuso",
                "grid_connection": "low_voltage"
            },
            "billing_settings": {
                "tariff_type": "time_of_use",
                "settlement_frequency": "monthly"
            }
        },
        {
            "name": "Wind Energy Cooperative Turin",
            "description": "Community wind energy project in Turin region",
            "legal_type": CERLegalType.COOPERATIVE,
            "type": CERType.ACTIVE,
            "status": CERStatus.ACTIVE,
            "address": "Corso Vittorio Emanuele II 90, 10121 Torino, TO",
            "region": "Piedmont",
            "province": "TO",
            "municipality": "Torino",
            "primary_substation_id": "SUB-TO-002",
            "total_capacity": 180.0,
            "energy_source": "wind",
            "pnrr_funding_applied": False,
            "gse_compliance_status": "pending",
            "technical_info": {
                "max_members": 50,
                "sharing_model": "autoconsumo_diffuso"
            }
        },
        {
            "name": "Mixed Energy Community Rome",
            "description": "Diverse renewable energy sources community in Rome",
            "legal_type": CERLegalType.ASSOCIATION,
            "type": CERType.ACTIVE,
            "status": CERStatus.PENDING,
            "address": "Via del Corso 126, 00186 Roma, RM",
            "region": "Lazio",
            "province": "RM",
            "municipality": "Roma",
            "primary_substation_id": "SUB-RM-003",
            "total_capacity": 320.0,
            "energy_source": "mixed",
            "pnrr_funding_applied": True,
            "pnrr_funding_status": "under_review",
            "gse_compliance_status": "pending",
            "technical_info": {
                "max_members": 150,
                "sources": ["solar", "wind", "biomass"]
            }
        }
    ]
    
    cers = []
    for cer_info in cer_data:
        cer = db.query(CER).filter(
            CER.name == cer_info["name"],
            CER.tenant_id == tenant_id
        ).first()
        
        if not cer:
            cer = CER(
                tenant_id=tenant_id,
                created_by=user_id,
                **cer_info
            )
            db.add(cer)
            db.flush()
            print(f"  ✓ Created CER: {cer.name} (ID: {cer.id})")
        else:
            print(f"  → CER already exists: {cer.name} (ID: {cer.id})")
        cers.append(cer)
    
    db.commit()
    
    # 2. Create Plants and link to CERs
    print("\n🏭 Creating Plants and linking to CERs...")
    plant_data = [
        {
            "name": "Solar Farm Milan North",
            "cer_id": cers[0].id,
            "type": PlantTypeEnum.PHOTOVOLTAIC,
            "status": PlantStatusEnum.IN_OPERATION,
            "power_kw": 150.0,
            "address": "Via Milano Nord 15, 20100 Milano"
        },
        {
            "name": "Solar Array Milan Center",
            "cer_id": cers[0].id,
            "type": PlantTypeEnum.PHOTOVOLTAIC,
            "status": PlantStatusEnum.IN_OPERATION,
            "power_kw": 100.0,
            "address": "Via Centro 45, 20121 Milano"
        },
        {
            "name": "Wind Farm Turin Hills",
            "cer_id": cers[1].id,
            "type": PlantTypeEnum.WIND,
            "status": PlantStatusEnum.IN_OPERATION,
            "power_kw": 180.0,
            "address": "Via Colline 12, 10125 Torino"
        },
        {
            "name": "Solar Park Rome East",
            "cer_id": cers[2].id,
            "type": PlantTypeEnum.PHOTOVOLTAIC,
            "status": PlantStatusEnum.IN_OPERATION,
            "power_kw": 200.0,
            "address": "Via Roma Est 88, 00100 Roma"
        },
        {
            "name": "Biomass Plant Rome",
            "cer_id": cers[2].id,
            "type": PlantTypeEnum.BIOMASS,
            "status": PlantStatusEnum.IN_OPERATION,
            "power_kw": 120.0,
            "address": "Via Biomassa 33, 00100 Roma"
        }
    ]
    
    plants = []
    for plant_info in plant_data:
        plant = db.query(Plant).filter(
            Plant.name == plant_info["name"],
            Plant.tenant_id == tenant_id
        ).first()
        
        if not plant:
            plant = Plant(
                tenant_id=tenant_id,
                created_by=user_id,
                **plant_info
            )
            db.add(plant)
            db.flush()
            print(f"  ✓ Created Plant: {plant.name} (ID: {plant.id}) → CER {plant.cer_id}")
        else:
            plant.cer_id = plant_info["cer_id"]
            db.commit()
            print(f"  → Linked existing Plant: {plant.name} → CER {plant.cer_id}")
        plants.append(plant)
    
    db.commit()
    
    # 3. Create CER Members
    print("\n👥 Creating CER Members...")
    member_data = [
        # CER 1 (Solar Community Milan) - Members
        {
            "cer_id": cers[0].id,
            "name": "Giuseppe Rossi",
            "address": "Via Garibaldi 12, 20121 Milano",
            "member_type": "prosumer",
            "pod_id": "IT001E12345678",
            "load_profile_type": "residential",
            "contracted_power": 3.0,
            "user_type": "real",
            "status": "active",
            "fiscal_code": "RSSGPP80A01H501X",
            "smart_meter_id": "SM-MI-001",
            "meter_type": "2G",
            "voltage_level": "230V",
            "activation_date": datetime.now(timezone.utc) - timedelta(days=180),
            "technical_info": {
                "plant_capacity": 5.0,
                "has_storage": True,
                "storage_capacity": 10.0,
                "is_incentivized": True,
                "capital_contribution": 15.0
            },
            "energy_produced": 1200.5,
            "energy_consumed": 850.3,
            "energy_shared": 350.2
        },
        {
            "cer_id": cers[0].id,
            "name": "Maria Bianchi",
            "address": "Via Dante 45, 20121 Milano",
            "member_type": "producer",
            "pod_id": "IT001E12345679",
            "load_profile_type": "residential",
            "contracted_power": 4.5,
            "user_type": "real",
            "status": "active",
            "fiscal_code": "BNCMRA75B02H501Y",
            "smart_meter_id": "SM-MI-002",
            "meter_type": "2G",
            "voltage_level": "230V",
            "activation_date": datetime.now(timezone.utc) - timedelta(days=150),
            "technical_info": {
                "plant_capacity": 8.0,
                "has_storage": False,
                "is_incentivized": True,
                "capital_contribution": 25.0
            },
            "energy_produced": 2400.8,
            "energy_consumed": 200.0,
            "energy_shared": 2200.8
        },
        {
            "cer_id": cers[0].id,
            "name": "Tech Startup Milano SRL",
            "address": "Via Brera 78, 20121 Milano",
            "member_type": "consumer",
            "pod_id": "IT001E12345680",
            "load_profile_type": "commercial",
            "contracted_power": 25.0,
            "user_type": "real",
            "status": "active",
            "vat_number": "IT12345678901",
            "smart_meter_id": "SM-MI-003",
            "meter_type": "2G",
            "voltage_level": "400V",
            "activation_date": datetime.now(timezone.utc) - timedelta(days=120),
            "energy_produced": 0.0,
            "energy_consumed": 4500.2,
            "energy_shared": -4500.2
        },
        # CER 2 (Wind Energy Cooperative Turin) - Members
        {
            "cer_id": cers[1].id,
            "name": "Antonio Verdi",
            "address": "Via Po 34, 10121 Torino",
            "member_type": "prosumer",
            "pod_id": "IT001E12345681",
            "load_profile_type": "residential",
            "contracted_power": 3.0,
            "user_type": "real",
            "status": "active",
            "fiscal_code": "VRDNTN70C03L219Z",
            "smart_meter_id": "SM-TO-001",
            "meter_type": "2G",
            "activation_date": datetime.now(timezone.utc) - timedelta(days=90),
            "technical_info": {
                "plant_capacity": 6.0,
                "has_storage": True,
                "storage_capacity": 12.0
            },
            "energy_produced": 1800.0,
            "energy_consumed": 1200.0,
            "energy_shared": 600.0
        },
        {
            "cer_id": cers[1].id,
            "name": "Residential Building Turin",
            "address": "Corso Francia 120, 10129 Torino",
            "member_type": "consumer",
            "pod_id": "IT001E12345682",
            "load_profile_type": "residential",
            "contracted_power": 10.0,
            "user_type": "real",
            "status": "active",
            "activation_date": datetime.now(timezone.utc) - timedelta(days=60),
            "energy_produced": 0.0,
            "energy_consumed": 3200.5,
            "energy_shared": -3200.5
        },
        # CER 3 (Mixed Energy Community Rome) - Members
        {
            "cer_id": cers[2].id,
            "name": "Francesca Neri",
            "address": "Via Trastevere 56, 00153 Roma",
            "member_type": "producer",
            "pod_id": "IT001E12345683",
            "load_profile_type": "residential",
            "contracted_power": 5.0,
            "user_type": "real",
            "status": "pending",
            "fiscal_code": "NRIFRC85D04H501W",
            "activation_date": datetime.now(timezone.utc) - timedelta(days=30),
            "technical_info": {
                "plant_capacity": 12.0,
                "is_incentivized": True
            },
            "energy_produced": 500.0,
            "energy_consumed": 100.0,
            "energy_shared": 400.0
        }
    ]
    
    members = []
    for member_info in member_data:
        member = db.query(CERMember).filter(
            CERMember.pod_id == member_info["pod_id"],
            CERMember.tenant_id == tenant_id
        ).first()
        
        if not member:
            member = CERMember(
                tenant_id=tenant_id,
                created_by=user_id,
                **member_info
            )
            db.add(member)
            db.flush()
            print(f"  ✓ Created Member: {member.name} ({member.member_type}) → CER {member.cer_id}")
        else:
            print(f"  → Member already exists: {member.name}")
        members.append(member)
    
    db.commit()
    
    # 4. Create CER Member Assets
    print("\n⚡ Creating CER Member Assets...")
    asset_data = [
        # Assets for Giuseppe Rossi (prosumer)
        {
            "member_id": members[0].id,
            "cer_id": cers[0].id,
            "name": "Rooftop Solar Panels - Giuseppe",
            "asset_type": CERMemberAssetType.SOLAR,
            "capacity": 5.0,
            "installation_date": datetime.now(timezone.utc) - timedelta(days=180),
            "gse_registration_id": "GSE-SOL-2023-001",
            "status": CERMemberAssetStatus.ACTIVE,
            "asset_metadata": {
                "panel_type": "monocrystalline",
                "inverter_model": "SMA Sunny Boy 5.0",
                "orientation": "south",
                "tilt_angle": 30
            }
        },
        {
            "member_id": members[0].id,
            "cer_id": cers[0].id,
            "name": "Battery Storage System",
            "asset_type": CERMemberAssetType.STORAGE,
            "capacity": 10.0,
            "installation_date": datetime.now(timezone.utc) - timedelta(days=150),
            "status": CERMemberAssetStatus.ACTIVE,
            "asset_metadata": {
                "battery_type": "lithium-ion",
                "manufacturer": "Tesla",
                "model": "Powerwall 2"
            }
        },
        # Assets for Maria Bianchi (producer)
        {
            "member_id": members[1].id,
            "cer_id": cers[0].id,
            "name": "Ground Mount Solar Array",
            "asset_type": CERMemberAssetType.SOLAR,
            "capacity": 8.0,
            "installation_date": datetime.now(timezone.utc) - timedelta(days=150),
            "gse_registration_id": "GSE-SOL-2023-002",
            "status": CERMemberAssetStatus.ACTIVE,
            "asset_metadata": {
                "panel_type": "polycrystalline",
                "inverter_model": "Fronius Symo 8.0",
                "orientation": "south-east",
                "tilt_angle": 25
            }
        },
        # Assets for Antonio Verdi (prosumer)
        {
            "member_id": members[3].id,
            "cer_id": cers[1].id,
            "name": "Residential Solar Installation",
            "asset_type": CERMemberAssetType.SOLAR,
            "capacity": 6.0,
            "installation_date": datetime.now(timezone.utc) - timedelta(days=90),
            "gse_registration_id": "GSE-SOL-2023-003",
            "status": CERMemberAssetStatus.ACTIVE,
            "asset_metadata": {
                "panel_type": "monocrystalline",
                "inverter_model": "Huawei SUN2000",
                "orientation": "south",
                "tilt_angle": 35
            }
        },
        {
            "member_id": members[3].id,
            "cer_id": cers[1].id,
            "name": "Home Battery System",
            "asset_type": CERMemberAssetType.STORAGE,
            "capacity": 12.0,
            "installation_date": datetime.now(timezone.utc) - timedelta(days=80),
            "status": CERMemberAssetStatus.ACTIVE,
            "asset_metadata": {
                "battery_type": "lithium-ion",
                "manufacturer": "LG Chem",
                "model": "RESU10H"
            }
        },
        # Assets for Francesca Neri (producer)
        {
            "member_id": members[5].id,
            "cer_id": cers[2].id,
            "name": "Large Solar Installation",
            "asset_type": CERMemberAssetType.SOLAR,
            "capacity": 12.0,
            "installation_date": datetime.now(timezone.utc) - timedelta(days=30),
            "gse_registration_id": "GSE-SOL-2023-004",
            "status": CERMemberAssetStatus.ACTIVE,
            "asset_metadata": {
                "panel_type": "monocrystalline",
                "inverter_model": "SMA Tripower 12.0",
                "orientation": "south",
                "tilt_angle": 30
            }
        }
    ]
    
    for asset_info in asset_data:
        asset = db.query(CERMemberAsset).filter(
            CERMemberAsset.name == asset_info["name"],
            CERMemberAsset.tenant_id == tenant_id
        ).first()
        
        if not asset:
            asset = CERMemberAsset(
                tenant_id=tenant_id,
                created_by=user_id,
                **asset_info
            )
            db.add(asset)
            print(f"  ✓ Created Asset: {asset.name} ({asset.asset_type}) → Member {asset.member_id}")
    
    db.commit()
    
    # 5. Create Participation Requests
    print("\n📝 Creating Participation Requests...")
    request_data = [
        {
            "cer_id": cers[0].id,
            "user_id": user_id,
            "status": ParticipationRequestStatus.PENDING,
            "request_date": datetime.now(timezone.utc) - timedelta(days=10),
            "notes": "Interested in joining as a prosumer with 8kW solar installation"
        },
        {
            "cer_id": cers[0].id,
            "user_id": user_id,
            "status": ParticipationRequestStatus.APPROVED,
            "request_date": datetime.now(timezone.utc) - timedelta(days=20),
            "processed_date": datetime.now(timezone.utc) - timedelta(days=15),
            "notes": "Approved membership for residential consumer"
        },
        {
            "cer_id": cers[1].id,
            "user_id": user_id,
            "status": ParticipationRequestStatus.PENDING,
            "request_date": datetime.now(timezone.utc) - timedelta(days=5),
            "notes": "Waiting for approval to join wind energy community"
        },
        {
            "cer_id": cers[2].id,
            "user_id": user_id,
            "status": ParticipationRequestStatus.REJECTED,
            "request_date": datetime.now(timezone.utc) - timedelta(days=30),
            "processed_date": datetime.now(timezone.utc) - timedelta(days=25),
            "notes": "Rejected due to location outside community boundary"
        }
    ]
    
    for req_info in request_data:
        # Check if request already exists
        existing = db.query(CERParticipationRequest).filter(
            CERParticipationRequest.cer_id == req_info["cer_id"],
            CERParticipationRequest.user_id == req_info["user_id"],
            CERParticipationRequest.request_date == req_info["request_date"]
        ).first()
        
        if not existing:
            request = CERParticipationRequest(
                tenant_id=tenant_id,
                created_by=user_id,
                **req_info
            )
            db.add(request)
            print(f"  ✓ Created Participation Request: CER {request.cer_id} - Status: {request.status.value}")
    
    db.commit()
    
    # 6. Create Compliance Requirements (CER and Plant)
    print("\n📋 Creating Compliance Requirements...")
    
    # CER Compliance Requirements
    cer_requirements_data = [
        {
            "cer_id": cers[0].id,
            "name": "GSE Annual Report Submission",
            "description": "Submit annual energy production and sharing report to GSE",
            "type": ComplianceTypeEnum.ANNUAL,
            "frequency_days": 365,
            "authority": "GSE",
            "portal_name": "GSE Portal",
            "requirement_data": {"deadline": "end_of_year"}
        },
        {
            "cer_id": cers[0].id,
            "name": "ARERA Energy Sharing Declaration",
            "description": "Quarterly declaration of energy sharing activities",
            "type": ComplianceTypeEnum.QUARTERLY,
            "frequency_days": 90,
            "authority": "ARERA",
            "portal_name": "ARERA Portal"
        },
        {
            "cer_id": cers[1].id,
            "name": "GSE Registration Renewal",
            "description": "Renew GSE registration for wind energy community",
            "type": ComplianceTypeEnum.ANNUAL,
            "frequency_days": 365,
            "authority": "GSE",
            "portal_name": "GSE Portal"
        }
    ]
    
    # Plant Compliance Requirements
    plant_requirements_data = [
        {
            "plant_id": plants[0].id,
            "name": "Photovoltaic Plant GSE Registration",
            "description": "Register photovoltaic plant with GSE",
            "type": ComplianceTypeEnum.ONE_TIME,
            "authority": "GSE",
            "portal_name": "Gaudì Portal",
            "requirement_data": {"registration_type": "photovoltaic"}
        },
        {
            "plant_id": plants[0].id,
            "name": "Annual Maintenance Report",
            "description": "Submit annual maintenance and performance report",
            "type": ComplianceTypeEnum.ANNUAL,
            "frequency_days": 365,
            "authority": "DSO",
            "portal_name": "DSO Portal"
        },
        {
            "plant_id": plants[2].id,
            "name": "Wind Farm Environmental Compliance",
            "description": "Quarterly environmental impact assessment",
            "type": ComplianceTypeEnum.QUARTERLY,
            "frequency_days": 90,
            "authority": "ADM",
            "portal_name": "ADM Portal"
        }
    ]
    
    all_requirements = []
    
    for req_info in cer_requirements_data + plant_requirements_data:
        req = ComplianceRequirement(
            tenant_id=tenant_id,
            created_by=user_id,
            **req_info
        )
        db.add(req)
        db.flush()
        all_requirements.append(req)
        entity_type = "CER" if req.cer_id else "Plant"
        entity_id = req.cer_id or req.plant_id
        print(f"  ✓ Created Requirement: {req.name} → {entity_type} {entity_id}")
    
    db.commit()
    
    # 7. Create Compliance Records
    print("\n📊 Creating Compliance Records...")
    
    from app.services.compliance_service import compliance_service
    
    records_created = 0
    for req in all_requirements:
        # Create records for requirements
        due_date = datetime.now(timezone.utc) + timedelta(days=30)
        
        # Some overdue records
        if req.name.startswith("GSE"):
            due_date = datetime.now(timezone.utc) - timedelta(days=10)
        
        record = ComplianceRecord(
            tenant_id=tenant_id,
            created_by=user_id,
            requirement_id=req.id,
            status=ComplianceStatusEnum.PENDING if due_date > datetime.now(timezone.utc) else ComplianceStatusEnum.OVERDUE,
            due_date=due_date,
            plant_id=req.plant_id,
            cer_id=req.cer_id,
            notes=f"Compliance record for {req.name}"
        )
        db.add(record)
        records_created += 1
    
    db.commit()
    print(f"  ✓ Created {records_created} Compliance Records")
    
    # 8. Create Documents
    print("\n📄 Creating Documents...")
    
    document_data = [
        {
            "cer_id": cers[0].id,
            "name": "GSE Registration Certificate",
            "file_name": "gse_registration.pdf",
            "file_path": "/documents/cer1/gse_registration.pdf",
            "type": DocumentTypeEnum.CERTIFICATE,
            "status": DocumentStatusEnum.APPROVED,
            "expiry_date": datetime.now(timezone.utc) + timedelta(days=300),
            "upload_date": datetime.now(timezone.utc) - timedelta(days=30),
            "document_metadata": {"document_number": "GSE-CER-2023-001"}
        },
        {
            "cer_id": cers[0].id,
            "name": "Community Bylaws",
            "file_name": "bylaws.pdf",
            "file_path": "/documents/cer1/bylaws.pdf",
            "type": DocumentTypeEnum.OTHER,
            "status": DocumentStatusEnum.APPROVED,
            "upload_date": datetime.now(timezone.utc) - timedelta(days=60),
            "document_metadata": {"version": "1.0"}
        },
        {
            "cer_id": cers[0].id,
            "name": "ARERA Compliance Report Q1",
            "file_name": "arera_q1_2024.pdf",
            "file_path": "/documents/cer1/arera_q1_2024.pdf",
            "type": DocumentTypeEnum.REPORT,
            "status": DocumentStatusEnum.APPROVED,
            "expiry_date": datetime.now(timezone.utc) + timedelta(days=60),
            "upload_date": datetime.now(timezone.utc) - timedelta(days=15),
            "document_metadata": {"quarter": "Q1", "year": 2024}
        },
        {
            "plant_id": plants[0].id,
            "name": "Plant Installation Certificate",
            "file_name": "installation_cert.pdf",
            "file_path": "/documents/plant1/installation_cert.pdf",
            "type": DocumentTypeEnum.CERTIFICATE,
            "status": DocumentStatusEnum.APPROVED,
            "expiry_date": datetime.now(timezone.utc) + timedelta(days=180),
            "upload_date": datetime.now(timezone.utc) - timedelta(days=90),
            "document_metadata": {"certificate_number": "CERT-PLANT-001"}
        },
        {
            "plant_id": plants[0].id,
            "name": "Maintenance Log 2024",
            "file_name": "maintenance_2024.pdf",
            "file_path": "/documents/plant1/maintenance_2024.pdf",
            "type": DocumentTypeEnum.REPORT,
            "status": DocumentStatusEnum.APPROVED,
            "upload_date": datetime.now(timezone.utc) - timedelta(days=20),
            "document_metadata": {"year": 2024, "type": "maintenance"}
        },
        {
            "cer_id": cers[1].id,
            "name": "Wind Farm Authorization",
            "file_name": "wind_authorization.pdf",
            "file_path": "/documents/cer2/wind_authorization.pdf",
            "type": DocumentTypeEnum.PERMIT,
            "status": DocumentStatusEnum.APPROVED,
            "expiry_date": datetime.now(timezone.utc) + timedelta(days=20),  # Expiring soon
            "upload_date": datetime.now(timezone.utc) - timedelta(days=200),
            "document_metadata": {"permit_number": "PERMIT-WIND-001"}
        }
    ]
    
    for doc_info in document_data:
        doc = Document(
            tenant_id=tenant_id,
            created_by=user_id,
            **doc_info
        )
        db.add(doc)
        entity_type = "CER" if doc.cer_id else "Plant"
        entity_id = doc.cer_id or doc.plant_id
        print(f"  ✓ Created Document: {doc.name} → {entity_type} {entity_id}")
    
    db.commit()
    
    # Summary
    print("\n" + "="*60)
    print("✅ CER Seed Data Summary")
    print("="*60)
    print(f"  CERs: {len(cers)}")
    print(f"  Plants: {len(plants)}")
    print(f"  Members: {len(members)}")
    print(f"  Member Assets: {len(asset_data)}")
    print(f"  Participation Requests: {len(request_data)}")
    print(f"  Compliance Requirements: {len(all_requirements)}")
    print(f"  Compliance Records: {records_created}")
    print(f"  Documents: {len(document_data)}")
    print("="*60)
    print("\n✨ Seed data creation complete!")


if __name__ == "__main__":
    db: Session = next(get_db())
    try:
        seed_cer_data(db)
    except Exception as e:
        print(f"\n❌ Error seeding CER data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

