# Modular Architecture: CER, Plant, Compliance

**Date**: January 2025  
**Design Principle**: **3 Independent Modules, Fully Interconnected, Usable Singly**

---

## 🎯 Architecture Principles

1. **Modularity**: Each module can function independently
2. **Interconnection**: Modules communicate through well-defined interfaces
3. **Standalone Capability**: Any module can be used without others
4. **Clear Boundaries**: Each module has its own API namespace and service layer

---

## 📦 Module Structure

```
kronos-eam-consolidated/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── plant.py          # PLANT MODULE
│   │   │   ├── cer.py            # CER MODULE
│   │   │   ├── compliance.py     # COMPLIANCE MODULE
│   │   │   └── document.py       # SHARED (used by all)
│   │   ├── services/
│   │   │   ├── plant_service.py  # PLANT MODULE
│   │   │   ├── cer_service.py   # CER MODULE
│   │   │   ├── compliance_service.py  # COMPLIANCE MODULE
│   │   │   └── interconnection_service.py  # INTERCONNECTION LAYER
│   │   ├── api/v1/endpoints/
│   │   │   ├── plants.py         # PLANT MODULE API
│   │   │   ├── cer.py            # CER MODULE API
│   │   │   ├── compliance.py     # COMPLIANCE MODULE API
│   │   │   └── documents.py      # SHARED API
│   │   └── schemas/
│   │       ├── plant.py
│   │       ├── cer.py
│   │       └── compliance.py
```

---

## 🔌 Module 1: PLANT MODULE

### Purpose
Manage power plants independently or as part of a CER.

### Core Capabilities
- ✅ Plant CRUD operations
- ✅ Asset management (linked to plants)
- ✅ Plant monitoring and statistics
- ✅ Plant metadata management
- ✅ Plant status tracking

### Standalone Usage
```python
# Can be used WITHOUT CER or Compliance
POST /api/v1/plants
GET  /api/v1/plants/{id}
PUT  /api/v1/plants/{id}
DELETE /api/v1/plants/{id}
GET  /api/v1/plants/{id}/assets
```

### Interconnection Points
```python
# Link to CER (optional)
POST /api/v1/plants/{id}/link-cer/{cer_id}
DELETE /api/v1/plants/{id}/unlink-cer

# Link to Compliance (optional)
GET /api/v1/plants/{id}/compliance
POST /api/v1/compliance/requirements (with plant_id)

# Link to Documents (optional)
GET /api/v1/documents?plant_id={id}
POST /api/v1/documents (with plant_id)
```

### API Endpoints
```
PLANT MODULE API (/api/v1/plants)
├── GET    /                        # List plants
├── POST   /                        # Create plant
├── GET    /{id}                    # Get plant details
├── PUT    /{id}                    # Update plant
├── DELETE /{id}                    # Delete plant
├── GET    /{id}/stats              # Plant statistics
├── GET    /{id}/assets             # List plant assets
├── POST   /{id}/assets              # Create asset
├── POST   /{id}/link-cer/{cer_id}  # Link to CER
└── DELETE /{id}/unlink-cer         # Unlink from CER
```

---

## ⚡ Module 2: CER MODULE

### Purpose
Manage Renewable Energy Communities independently or with linked plants.

### Core Capabilities
- ✅ CER CRUD operations
- ✅ Member management
- ✅ Boundary management (PostGIS)
- ✅ Energy sharing calculations
- ✅ Billing and transactions
- ✅ Participation requests
- ✅ Simulation tools

### Standalone Usage
```python
# Can be used WITHOUT Plants or Compliance
POST /api/v1/cer/communities
GET  /api/v1/cer/communities/{id}
POST /api/v1/cer/communities/{id}/members
GET  /api/v1/cer/communities/{id}/energy/shared
```

### Interconnection Points
```python
# Link to Plants (optional)
GET  /api/v1/cer/communities/{id}/plants
POST /api/v1/plants/{id}/link-cer/{cer_id}

# Link to Compliance (optional)
GET  /api/v1/cer/communities/{id}/compliance
POST /api/v1/compliance/cer/{id}/submit

# Link to Documents (optional)
GET  /api/v1/documents?cer_id={id}
POST /api/v1/documents (with cer_id)
```

### API Endpoints
```
CER MODULE API (/api/v1/cer)
├── communities/
│   ├── GET    /                    # List CERs
│   ├── POST   /                    # Create CER
│   ├── GET    /{id}                # Get CER details
│   ├── PUT    /{id}                # Update CER
│   ├── DELETE /{id}                # Delete CER
│   ├── members/
│   │   ├── GET    /                # List members
│   │   ├── POST   /                # Add member
│   │   ├── PUT    /{mid}           # Update member
│   │   └── DELETE /{mid}           # Remove member
│   ├── plants/                     # INTERCONNECTION: Plants
│   │   └── GET    /                # List linked plants
│   ├── energy/                     # Energy sharing
│   │   ├── GET    /shared          # Shared energy calc
│   │   ├── GET    /transactions    # Energy transactions
│   │   └── POST   /calculate       # Calculate sharing
│   ├── billing/                    # Billing & financial
│   │   ├── GET    /                # Billing overview
│   │   ├── GET    /transactions    # Transactions
│   │   └── POST   /settle          # Settlement calc
│   ├── compliance/                 # INTERCONNECTION: Compliance
│   │   ├── GET    /                # Compliance status
│   │   └── POST   /submit          # Submit compliance
│   └── simulation/                 # Simulation tools
│       ├── POST   /run             # Run simulation
│       └── GET    /results         # Get results
└── participation-requests/         # Join requests
    ├── GET    /                    # List requests
    ├── POST   /                    # Create request
    ├── GET    /{id}                # Get request
    ├── PUT    /{id}                # Approve/reject
    └── DELETE /{id}                # Delete request
```

---

## 📋 Module 3: COMPLIANCE MODULE

### Purpose
Manage compliance requirements independently or linked to plants/CERs.

### Core Capabilities
- ✅ Compliance requirement management
- ✅ Compliance record tracking
- ✅ Document management
- ✅ Status tracking (pending, completed, overdue)
- ✅ Penalty tracking

### Standalone Usage
```python
# Can be used WITHOUT Plants or CER
GET  /api/v1/compliance/requirements
POST /api/v1/compliance/requirements
GET  /api/v1/compliance/records
GET  /api/v1/compliance/overdue
```

### Interconnection Points
```python
# Link to Plants (optional)
GET  /api/v1/compliance/plants/{id}
POST /api/v1/compliance/requirements (with plant_id)

# Link to CER (optional)
GET  /api/v1/compliance/cer/{id}
POST /api/v1/compliance/cer/{id}/submit

# Link to Documents (required for compliance)
GET  /api/v1/documents?compliance_id={id}
POST /api/v1/documents (with compliance_record_id)
```

### API Endpoints
```
COMPLIANCE MODULE API (/api/v1/compliance)
├── requirements/
│   ├── GET    /                    # List requirements
│   ├── POST   /                    # Create requirement
│   ├── GET    /{id}                # Get requirement
│   ├── PUT    /{id}                # Update requirement
│   └── DELETE /{id}                # Delete requirement
├── records/
│   ├── GET    /                    # List records
│   ├── GET    /{id}                # Get record
│   ├── POST   /{id}/complete       # Mark complete
│   └── PUT    /{id}                # Update record
├── overdue/                        # Overdue tracking
│   └── GET    /                    # List overdue
├── plants/{id}/                    # INTERCONNECTION: Plants
│   └── GET    /                    # Plant compliance
└── cer/{id}/                       # INTERCONNECTION: CER
    ├── GET    /                    # CER compliance
    └── POST   /submit              # Submit CER compliance
```

---

## 🔗 Interconnection Layer

### Purpose
Manage relationships between modules without tight coupling.

### Implementation
```python
# app/services/interconnection_service.py

class InterconnectionService:
    """Service for cross-module operations"""
    
    @staticmethod
    def link_plant_to_cer(db: Session, plant_id: int, cer_id: int, tenant_id: str):
        """Link plant to CER with validation"""
        # Validate plant exists
        plant = plant_service.get_plant(db, plant_id, tenant_id)
        if not plant:
            raise ValueError("Plant not found")
        
        # Validate CER exists
        cer = cer_service.get_cer(db, cer_id, tenant_id)
        if not cer:
            raise ValueError("CER not found")
        
        # Validate plant location is within CER boundary
        if cer.boundary:
            if not validate_plant_in_boundary(plant, cer.boundary):
                raise ValueError("Plant location is outside CER boundary")
        
        # Link plant to CER
        plant.cer_id = cer_id
        db.commit()
        
        # Update CER capacity
        cer_service._update_capacity(db, cer_id, tenant_id)
        
        return plant
    
    @staticmethod
    def link_compliance_to_plant(db: Session, requirement_id: int, plant_id: int, tenant_id: str):
        """Link compliance requirement to plant"""
        requirement = compliance_service.get_requirement(db, requirement_id, tenant_id)
        if not requirement:
            raise ValueError("Requirement not found")
        
        plant = plant_service.get_plant(db, plant_id, tenant_id)
        if not plant:
            raise ValueError("Plant not found")
        
        requirement.plant_id = plant_id
        db.commit()
        
        return requirement
    
    @staticmethod
    def link_compliance_to_cer(db: Session, requirement_id: int, cer_id: int, tenant_id: str):
        """Link compliance requirement to CER"""
        requirement = compliance_service.get_requirement(db, requirement_id, tenant_id)
        if not requirement:
            raise ValueError("Requirement not found")
        
        cer = cer_service.get_cer(db, cer_id, tenant_id)
        if not cer:
            raise ValueError("CER not found")
        
        requirement.cer_id = cer_id
        db.commit()
        
        return requirement
```

---

## 📊 Module Dependencies

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    PLANT    │     │     CER     │     │ COMPLIANCE  │
│   MODULE    │     │   MODULE    │     │   MODULE    │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                  ┌────────▼────────┐
                  │   DOCUMENTS     │
                  │   (SHARED)      │
                  └─────────────────┘
```

**Key Points**:
- No direct dependencies between Plant, CER, and Compliance
- All modules can use Documents independently
- Interconnections are optional and loosely coupled

---

## 🎯 Usage Scenarios

### Scenario 1: Plant Only (No CER, No Compliance)
```python
# Create plant
POST /api/v1/plants
{
  "name": "Solar Farm Alpha",
  "type": "photovoltaic",
  "power_kw": 1000.0
}

# Add assets
POST /api/v1/plants/1/assets
{
  "name": "Panel Array 1",
  "type": "solar_panel"
}

# Get plant stats
GET /api/v1/plants/1/stats
```

### Scenario 2: CER Only (No Plants, No Compliance)
```python
# Create CER
POST /api/v1/cer/communities
{
  "name": "Green Energy Community",
  "legal_type": "cooperative",
  "boundary": [...]
}

# Add members
POST /api/v1/cer/communities/1/members
{
  "name": "Member 1",
  "member_type": "consumer",
  "pod_id": "IT001E12345678"
}

# Calculate energy sharing
POST /api/v1/cer/communities/1/energy/calculate
```

### Scenario 3: Compliance Only (No Plants, No CER)
```python
# Create requirement
POST /api/v1/compliance/requirements
{
  "name": "GSE Annual Report",
  "type": "annual",
  "authority": "GSE"
}

# Create record
POST /api/v1/compliance/records
{
  "requirement_id": 1,
  "due_date": "2025-12-31"
}

# Get overdue
GET /api/v1/compliance/overdue
```

### Scenario 4: Full Integration (All Modules)
```python
# Create plant
POST /api/v1/plants
{
  "name": "Solar Farm Alpha",
  "type": "photovoltaic"
}

# Create CER
POST /api/v1/cer/communities
{
  "name": "Green Energy Community"
}

# Link plant to CER
POST /api/v1/plants/1/link-cer/1

# Create compliance requirement for plant
POST /api/v1/compliance/requirements
{
  "name": "Plant Registration",
  "plant_id": 1
}

# Create compliance requirement for CER
POST /api/v1/compliance/requirements
{
  "name": "GSE CER Report",
  "cer_id": 1
}

# Upload compliance document
POST /api/v1/documents
{
  "name": "GSE Report 2025",
  "compliance_record_id": 1,
  "cer_id": 1
}
```

---

## ✅ Implementation Checklist

### Phase 1: Core Modules (Done)
- [x] Plant Module - Basic CRUD
- [x] CER Module - Basic CRUD + Members
- [x] Compliance Module - Basic CRUD

### Phase 2: Interconnections (In Progress)
- [x] Plant ↔ CER linking
- [ ] Plant ↔ Compliance linking
- [ ] CER ↔ Compliance linking
- [ ] Documents ↔ All modules

### Phase 3: Missing CER Features (Pending)
- [ ] Participation Requests
- [ ] Energy Sharing Calculations
- [ ] Billing & Transactions
- [ ] Simulation Tools

### Phase 4: Enhanced Features (Future)
- [ ] Energy Optimization (MINLP)
- [ ] Advanced Analytics
- [ ] Forecasting Algorithms

---

## 📝 API Design Guidelines

1. **Module Prefix**: Each module has its own API prefix
   - `/api/v1/plants/*` - Plant module
   - `/api/v1/cer/*` - CER module
   - `/api/v1/compliance/*` - Compliance module

2. **Interconnection Endpoints**: Use sub-resources
   - `/api/v1/plants/{id}/cer` - Plant's CER
   - `/api/v1/cer/communities/{id}/plants` - CER's plants
   - `/api/v1/compliance/plants/{id}` - Plant compliance

3. **Query Parameters**: Support filtering by module relationships
   - `GET /api/v1/plants?cer_id={id}` - Plants in CER
   - `GET /api/v1/documents?plant_id={id}` - Plant documents
   - `GET /api/v1/documents?cer_id={id}` - CER documents

4. **Error Handling**: Clear errors for missing interconnections
   - `404` if linking to non-existent resource
   - `400` if validation fails (e.g., plant outside CER boundary)

---

**Next Steps**: Implement missing interconnections and CER features based on priority.

