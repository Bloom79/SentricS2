# Deep Consolidation Architecture Analysis

## Executive Summary

This document provides a comprehensive architectural analysis for consolidating:
1. **Site & Plant Management** (from Sentrics) - Multi-level hierarchy: Sites → Plants → Assets with visual canvas designer
2. **Asset Management** (from Sentrics) - Complex asset hierarchy with string configuration, bulk import, monitoring, and maintenance
3. **CER Management** (from Sentrics) - Renewable Energy Communities with geographic constraints
4. **Document Management** (from Kronos EAM) - Centralized document repository with workflow integration
5. **Workflow System** (from Kronos EAM) - Guided multi-phase regulatory processes
6. **Energy Flow & Visualization** (from Sentrics) - React Flow canvas for visual plant design and energy flow
7. **Financial Management** (from Sentrics) - Financial tracking per plant/site/consumer
8. **Grid Integration** (from Sentrics) - Terna grid exchange, file exchange, contracts
9. **Simulation & Forecasting** (from Sentrics) - Energy simulation, weather integration, forecasting

---

## 1. Domain Model Analysis

### 1.1 Core Entities and Their Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    CONSOLIDATED DOMAIN MODEL                 │
└─────────────────────────────────────────────────────────────┘

TENANT (Organization)
│
├── SITES (Physical Locations)
│   │
│   ├── PLANTS (Renewable Energy Installations per Site)
│   │   │
│   │   ├── PLANT REGISTRY (Technical Details)
│   │   │   ├── POD Code (DSO)
│   │   │   ├── GAUDÌ Code (Terna)
│   │   │   ├── CENSIMP Code (Municipality)
│   │   │   └── RID Number (GSE)
│   │   │
│   │   ├── PLANT LAYOUT (Visual Canvas Design)
│   │   │   ├── React Flow Nodes (Components)
│   │   │   ├── React Flow Edges (Connections)
│   │   │   └── Energy Flow Visualization
│   │   │
│   │   ├── ASSETS (Equipment Hierarchy)
│   │   │   ├── Solar Arrays
│   │   │   │   ├── String Configuration
│   │   │   │   ├── Panels per String
│   │   │   │   └── String Assignments
│   │   │   ├── Solar Panels (Individual)
│   │   │   │   ├── String Assignment
│   │   │   │   ├── Technical Specs
│   │   │   │   └── Bulk Import Support
│   │   │   ├── Wind Turbines
│   │   │   │   ├── Wind Turbine Clusters
│   │   │   │   ├── Rotor Diameter, Hub Height
│   │   │   │   └── Cut-in/Cut-out Speeds
│   │   │   ├── Inverters
│   │   │   │   ├── MPPT Channels
│   │   │   │   └── Efficiency Ratings
│   │   │   ├── Batteries (BESS)
│   │   │   │   ├── Capacity (kWh)
│   │   │   │   ├── Chemistry Type
│   │   │   │   └── Cycle Life
│   │   │   ├── Transformers
│   │   │   │   ├── Primary/Secondary Voltage
│   │   │   │   └── Rated Power (MVA)
│   │   │   ├── Collector Substations
│   │   │   │   ├── Voltage Level
│   │   │   │   └── Protection Type
│   │   │   ├── Grid Components
│   │   │   ├── Consumers
│   │   │   ├── SCADA Systems
│   │   │   └── Sensors
│   │   │
│   │   ├── ASSET MONITORING (Real-time Data)
│   │   │   ├── Performance Metrics
│   │   │   ├── Historical Trends
│   │   │   ├── Threshold Alerts
│   │   │   └── Anomaly Detection
│   │   │
│   │   ├── ASSET MAINTENANCE
│   │   │   ├── Maintenance Scheduling
│   │   │   ├── Maintenance Records
│   │   │   ├── Predictive Maintenance
│   │   │   └── Technician Assignments
│   │   │
│   │   └── STORAGE UNITS (BESS per Site)
│   │       ├── Capacity Tracking
│   │       ├── Charge/Discharge Cycles
│   │       └── State of Charge (SoC)
│   │
│   ├── CONSUMERS (Site-level)
│   │   ├── Consumer Profiles
│   │   ├── Consumption Tracking
│   │   └── Load Profiles
│   │
│   └── ENERGY FLOW (Site-level Visualization)
│       ├── React Flow Canvas
│       ├── Component Connections
│       ├── Real-time Flow Data
│       └── Fault Detection
│   │
│   ├── WORKFLOWS (Regulatory Processes)
│   │   ├── Activation Workflow (8 phases)
│   │   ├── Compliance Workflows (Annual)
│   │   ├── Fiscal Workflows
│   │   └── Maintenance Workflows
│   │
│   ├── DOCUMENTS (All Plant-Related Files)
│   │   ├── GSE Documents
│   │   ├── Terna Documents
│   │   ├── DSO Documents
│   │   ├── ADM Documents
│   │   └── Municipal Documents
│   │
│   └── COMPLIANCE REQUIREMENTS
│       ├── DSO Requirements
│       ├── Terna Requirements
│       ├── GSE Requirements
│       └── ADM Requirements
│
├── CER (Renewable Energy Communities)
│   │
│   ├── CER MEMBERS
│   │   ├── Plants (from Plant registry)
│   │   ├── POD Codes
│   │   ├── Load Profiles
│   │   └── Participation Status
│   │
│   ├── CER WORKFLOWS
│   │   ├── CER Constitution
│   │   ├── PNRR Application (40% funding)
│   │   ├── Member Onboarding
│   │   └── Annual Compliance
│   │
│   └── CER DOCUMENTS
│       ├── Legal Entity Documents
│       ├── Member Contracts
│       └── Energy Sharing Reports
│
└── USERS (Multi-Role Support)
    ├── Administrators
    ├── Asset Managers
    ├── Plant Owners
    ├── Technicians
    └── Compliance Officers
```

### 1.2 Portal Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  PORTAL INTEGRATION MAP                    │
└─────────────────────────────────────────────────────────────┘

GSE PORTAL (Energy Services Manager)
├── Purpose: Incentive management, RID applications
├── Integration Points:
│   ├── Plant → RID Application Workflow
│   ├── Plant → Annual Fuel Mix Disclosure
│   ├── Plant → Anti-Mafia Declaration
│   └── CER → Shared Production Tracking
├── Documents: Contracts, Conventions, Declarations
└── Workflows: Activation, Annual Compliance

TERNA PORTAL (GAUDÌ System)
├── Purpose: Grid connection, plant registration
├── Integration Points:
│   ├── Plant → GAUDÌ Registration
│   ├── Plant → Production Data Submission
│   └── Plant → Forecast Updates
├── Documents: Registration Forms, Technical Sheets
└── Workflows: Registration, Data Updates

DSO PORTAL (E-Distribuzione)
├── Purpose: Grid connection, technical compliance
├── Integration Points:
│   ├── Plant → Connection Request
│   ├── Plant → Technical Documentation
│   ├── Plant → Meter Installation
│   └── Plant → Protection System Checks
├── Documents: TICA, Technical Projects, Certificates
└── Workflows: Connection Request, Testing, Activation

ADM PORTAL (Customs Agency)
├── Purpose: Electric workshop licensing
├── Integration Points:
│   ├── Plant → UTF License Application
│   ├── Plant → Annual Consumption Declaration
│   └── Plant → License Fee Payment
├── Documents: UTF Licenses, Declarations, EDI Files
└── Workflows: Licensing, Annual Compliance

MUNICIPAL PORTALS (SUAP)
├── Purpose: Permits and authorizations
├── Integration Points:
│   ├── Plant → Building Permits
│   ├── Plant → Environmental Authorizations
│   └── Plant → Landscape Permits
├── Documents: Permits, Authorizations, Compliance Certificates
└── Workflows: Authorization Requests
```

---

## 2. Portal Areas and User Contexts

### 2.1 Plant Management Portal Area

**Primary Context**: Managing individual renewable energy installations

**Key Features**:
- **Plant Registry**: Master database of all installations
- **Technical Registry**: POD, GAUDÌ, CENSIMP, RID codes
- **Visual Plant Designer**: Drag-and-drop canvas for plant architecture (CRITICAL FEATURE)
- **Asset Management**: Equipment hierarchy and monitoring
- **Multi-Phase Process Guide**: 8-phase activation workflow
- **Portal Integration Tabs**: Dedicated sections for each portal
- **Compliance Dashboard**: Real-time compliance status across all portals

**Visual Plant Designer** (From Sentrics - React Flow):
- **Drag-and-Drop Canvas**: React Flow (@xyflow/react) for visual plant design
- **Component Palette**: Categorized components (Generation, Conversion, Storage, Consumption)
- **Visual Connections**: Draw connections between components (solar → inverter → transformer → grid)
- **Real-time Energy Flow**: Visualize energy flow through the system
- **Edit/View Modes**: Toggle between editing and viewing
- **Layout Persistence**: Save plant layout to database
- **Component Types**:
  - Generation: Solar Arrays, Solar Panels, Wind Turbines, Wind Turbine Clusters
  - Power Conversion: Inverters, Transformers, Collector Substations
  - Storage: Batteries (BESS)
  - Consumption: Consumers (Residential, Industrial)
  - Grid: Power Grid Connection
  - Monitoring: SCADA Systems, Sensors

**User Workflows**:
1. **Plant Creation** → Auto-assessment → Portal requirements identified
2. **Visual Plant Design** → Drag components → Connect → Save layout
3. **Activation Workflow** → Guided through 8 phases → Portal interactions
4. **Ongoing Compliance** → Annual workflows → Portal submissions
5. **Document Management** → Portal-specific documents → Version control

**UI Structure**:
```
Plant Detail Page
├── Overview Tab (Basic info, status, KPIs)
├── Visual Designer Tab (React Flow canvas - NEW!)
│   ├── Component Palette (Drag components)
│   ├── Canvas (Drop and connect components)
│   ├── Node Details Sidebar (Component properties)
│   ├── Edge Details (Connection properties)
│   └── Save/Load Layout
├── Registry Tab (POD, GAUDÌ, CENSIMP, RID)
├── Assets Tab (Equipment hierarchy, monitoring)
├── GSE Tab (RID status, conventions, declarations)
├── Terna Tab (GAUDÌ registration, production data)
├── DSO Tab (Connection status, technical docs)
├── Customs Tab (UTF license, declarations)
├── Compliance Tab (Overall status, requirements)
├── Workflows Tab (All plant workflows)
└── Documents Tab (All plant documents, filtered by portal)
```

### 2.2 CER Management Portal Area

**Primary Context**: Managing Renewable Energy Communities

**Key Features**:
- **CER Registry**: All communities with geographic boundaries
- **Member Management**: Producers, consumers, prosumers
- **Plant Linking**: Connect plants to CER
- **Energy Sharing**: Production allocation and billing
- **PNRR Support**: 40% funding application workflows
- **Geographic Visualization**: PostGIS boundaries and member locations

**User Workflows**:
1. **CER Creation** → Legal entity setup → Geographic definition
2. **Member Onboarding** → POD validation → Plant linking
3. **PNRR Application** → 40% funding workflow → Document submission
4. **Energy Management** → Production tracking → Billing calculations
5. **Annual Compliance** → Collective obligations → Portal submissions

**UI Structure**:
```
CER Detail Page
├── Overview Tab (Basic info, status, KPIs)
├── Geography Tab (Map view, boundaries, member locations)
├── Members Tab (Member list, POD validation, status)
├── Plants Tab (Linked plants, production capacity)
├── PNRR Tab (Funding application, status, documents)
├── Energy Sharing Tab (Production, consumption, billing)
├── Compliance Tab (CER-specific compliance)
├── Workflows Tab (CER workflows)
└── Documents Tab (CER documents)
```

### 2.3 Document Management Portal Area

**Primary Context**: Centralized document repository

**Key Features**:
- **Unified Repository**: All documents from all portals
- **Portal Filtering**: Filter by GSE, Terna, DSO, ADM, Municipal
- **Workflow Integration**: Documents linked to workflows and tasks
- **Version Control**: Complete version history
- **Expiration Tracking**: Automated alerts for expiring documents
- **AI Extraction**: Automatic data extraction from PDFs
- **Template Library**: Pre-filled forms for all portals

**User Workflows**:
1. **Document Upload** → Auto-categorization → Portal assignment
2. **Template Generation** → Pre-fill from plant data → Portal form
3. **Expiration Monitoring** → Alerts → Renewal workflow creation
4. **Version Management**:

```markdown
**Architecture Design**:
- AI-powered document extraction
- Portal-specific document templates
- Automated version control
- Cross-portal document search
```

---

## 3. Consolidated UI Architecture

### 3.1 Navigation Structure

```
Main Navigation
├── Dashboard (Portfolio overview)
├── Plants (Plant Management Portal)
│   ├── Plant List
│   ├── Plant Detail
│   │   ├── Overview
│   │   ├── Registry
│   │   ├── Assets
│   │   ├── GSE Portal
│   │   ├── Terna Portal
│   │   ├── DSO Portal
│   │   ├── Customs Portal
│   │   ├── Compliance
│   │   ├── Workflows
│   │   └── Documents
│   └── Process Guide (8-phase activation)
├── CER (CER Management Portal)
│   ├── CER List
│   ├── CER Detail
│   │   ├── Overview
│   │   ├── Geography
│   │   ├── Members
│   │   ├── Plants
│   │   ├── PNRR
│   │   ├── Energy Sharing
│   │   ├── Compliance
│   │   ├── Workflows
│   │   └── Documents
│   └── Member Management
├── Workflows (Cross-portal workflow management)
│   ├── Workflow Templates
│   ├── Active Workflows
│   └── Workflow History
├── Documents (Centralized Document Management)
│   ├── All Documents
│   ├── By Portal (GSE, Terna, DSO, ADM, Municipal)
│   ├── By Plant
│   ├── By CER
│   ├── Expiring Documents
│   └── Template Library
├── Compliance (Cross-portal compliance dashboard)
│   ├── Compliance Status
│   ├── Upcoming Deadlines
│   ├── Penalty Calculator
│   └── Compliance Reports
└── Administration
    ├── User Management
    ├── System Settings
    └── Integrations
```

### 3.2 Portal-Aware Context Switching

**Key Concept**: Users switch between "portal contexts" within the same plant/CER

**Implementation**:
- **Plant Detail** → Tabs for each portal → Context-aware workflows
- **CER Detail** → Tabs for CER-specific portals → Member and plant context
- **Document Library** → Portal filters → Context-aware templates
- **Workflow Templates** → Portal-specific templates → Auto-context

---

## 4. Backend Architecture Consolidation

### 4.1 Service Layer Organization

```
app/services/
├── plant_service.py (Enhanced)
│   ├── Plant CRUD
│   ├── Portal status methods (GSE, Terna, DSO, ADM)
│   ├── Asset management
│   └── Registry management
│
├── cer_service.py (From Sentrics)
│   ├── CER CRUD
│   ├── Member management
│   ├── Plant linking
│   ├── Energy sharing calculations
│   └── PNRR workflows
│
├── asset_service.py (From Sentrics)
│   ├── Asset CRUD
│   ├── Asset type management
│   ├── Asset hierarchy
│   └── Asset monitoring
│
├── workflow_service.py (Enhanced)
│   ├── Workflow CRUD
│   ├── Portal-specific workflow templates
│   ├── Multi-phase workflow management
│   └── Task assignment
│
├── document_service.py (Enhanced)
│   ├── Document CRUD
│   ├── Portal-aware document categorization
│   ├── Version control
│   ├── Expiration tracking
│   └── AI extraction integration
│
├── portal_service.py (NEW - Unified Portal Interface)
│   ├── Portal status checking
│   ├── Portal form generation
│   ├── Portal submission tracking
│   └── Portal-specific validations
│
└── compliance_service.py (Enhanced)
    ├── Compliance requirement tracking
    ├── Compliance score calculation
    ├── Deadline calculation
    └── Penalty calculation
```

### 4.2 Portal Integration Abstraction

**New Service**: `portal_service.py`

**Purpose**: Unified interface for all portal interactions

```python
class PortalService:
    """Unified portal integration service"""
    
    def get_portal_status(self, plant_id: int, portal: PortalType) -> PortalStatus:
        """Get status from any portal (GSE, Terna, DSO, ADM)"""
        pass
    
    def generate_portal_form(self, plant_id: int, portal: PortalType, form_type: str) -> FormData:
        """Generate pre-filled form for any portal"""
        pass
    
    def submit_to_portal(self, plant_id: int, portal: PortalType, data: dict) -> SubmissionResult:
        """Submit data to any portal (when API available)"""
        pass
    
    def get_portal_requirements(self, plant_id: int, portal: PortalType) -> List[Requirement]:
        """Get requirements for any portal"""
        pass
```

### 4.3 Plant Layout Service (NEW - For Visual Designer)

**New Service**: `plant_layout_service.py`

**Purpose**: Manage visual plant layouts and component connections

```python
class PlantLayoutService:
    """Service for managing visual plant layouts"""
    
    def save_plant_layout(
        self,
        plant_id: int,
        nodes: List[Node],
        edges: List[Edge],
        tenant_id: str
    ) -> PlantLayout:
        """Save plant visual layout (React Flow nodes and edges)"""
        pass
    
    def load_plant_layout(
        self,
        plant_id: int,
        tenant_id: str
    ) -> Optional[PlantLayout]:
        """Load saved plant layout"""
        pass
    
    def validate_layout(
        self,
        nodes: List[Node],
        edges: List[Edge]
    ) -> ValidationResult:
        """Validate plant layout (check connections, power flow)"""
        pass
    
    def generate_layout_from_assets(
        self,
        plant_id: int,
        tenant_id: str
    ) -> PlantLayout:
        """Auto-generate layout from existing assets"""
        pass
```

**New Model**: `plant_layout.py`

```python
class PlantLayout(BaseModel):
    """Plant visual layout model"""
    __tablename__ = "plant_layouts"
    
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False, unique=True)
    
    # React Flow data (stored as JSON)
    nodes = Column(JSON, nullable=False)  # List of React Flow nodes
    edges = Column(JSON, nullable=False)  # List of React Flow edges
    
    # Metadata
    version = Column(Integer, default=1)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    plant = relationship("Plant", back_populates="layout")
```

### 4.3 Enhanced Plant Model Relationships

```python
class Plant(BaseModel):
    # ... existing fields ...
    
    # Portal Integration Status
    gse_status = Column(JSON)  # RID status, convention status, etc.
    terna_status = Column(JSON)  # GAUDÌ status, registration date, etc.
    dso_status = Column(JSON)  # Connection status, meter info, etc.
    adm_status = Column(JSON)  # UTF license status, etc.
    
    # Relationships
    cer = relationship("CER", back_populates="plants")
    assets = relationship("Asset", back_populates="plant")
    workflows = relationship("Workflow", back_populates="plant")
    documents = relationship("Document", back_populates="plant")
    compliance_requirements = relationship("ComplianceRequirement", back_populates="plant")
```

---

## 5. Frontend Component Architecture

### 5.1 Portal-Aware Components

```
src/components/
├── portals/
│   ├── GSEPortal.tsx (GSE-specific UI)
│   ├── TernaPortal.tsx (Terna-specific UI)
│   ├── DSOPortal.tsx (DSO-specific UI)
│   ├── ADMPortal.tsx (ADM-specific UI)
│   └── MunicipalPortal.tsx (Municipal-specific UI)
│
├── plants/
│   ├── PlantDetail.tsx (Main container)
│   ├── PlantOverview.tsx
│   ├── PlantRegistry.tsx
│   ├── PlantVisualDesigner.tsx (NEW - React Flow canvas)
│   │   ├── FlowCanvas.tsx (Main canvas component)
│   │   ├── ComponentsPalette.tsx (Drag components)
│   │   ├── FlowNodeTypes.tsx (Node type definitions)
│   │   ├── FlowNodes/ (Individual node components)
│   │   │   ├── SolarPanelNode.tsx
│   │   │   ├── WindTurbineNode.tsx
│   │   │   ├── InverterNode.tsx
│   │   │   ├── TransformerNode.tsx
│   │   │   ├── BESSNode.tsx
│   │   │   ├── GridNode.tsx
│   │   │   └── ConsumerNode.tsx
│   │   ├── NodeDetailsSidebar.tsx (Component properties)
│   │   ├── EdgeDialog.tsx (Connection properties)
│   │   └── FlowControls.tsx (Zoom, pan, fit view)
│   ├── PlantAssets.tsx
│   ├── PlantCompliance.tsx
│   └── PlantWorkflows.tsx
│
├── cer/
│   ├── CERDetail.tsx (Main container)
│   ├── CERGeography.tsx (PostGIS map)
│   ├── CERMembers.tsx
│   ├── CERPlants.tsx
│   ├── CERNRNR.tsx
│   └── CEREnergySharing.tsx
│
├── documents/
│   ├── DocumentLibrary.tsx
│   ├── DocumentUpload.tsx
│   ├── DocumentViewer.tsx
│   ├── DocumentTemplate.tsx
│   └── DocumentExpirationAlerts.tsx
│
└── workflows/
    ├── WorkflowWizard.tsx (Multi-phase guide)
    ├── WorkflowPhase.tsx
    ├── WorkflowTask.tsx
    └── WorkflowTemplateSelector.tsx
```

### 5.2 Context Providers

```typescript
// Portal Context - Provides current portal context
<PortalProvider>
  <PlantDetail />
</PortalProvider>

// Plant Context - Provides current plant data
<PlantProvider>
  <PlantDetail />
</PlantProvider>

// CER Context - Provides current CER data
<CERProvider>
  <CERDetail />
</CERProvider>
```

---

## 6. Data Flow Architecture

### 6.1 Plant Creation Flow

```
1. User creates Plant
   ↓
2. System assesses portal requirements
   ├── GSE requirements (if power > threshold)
   ├── Terna requirements (always)
   ├── DSO requirements (always)
   └── ADM requirements (if applicable)
   ↓
3. System creates compliance requirements
   ↓
4. System suggests activation workflow
   ↓
5. User starts activation workflow
   ↓
6. Workflow guides through 8 phases
   ├── Each phase creates portal-specific tasks
   ├── Each task links to portal forms
   └── Each task collects documents
   ↓
7. Documents uploaded → Auto-categorized by portal
   ↓
8. Portal status updated → Compliance score recalculated
```

### 6.2 CER Creation Flow

```
1. User creates CER
   ↓
2. System defines geographic boundary (PostGIS)
   ↓
3. System validates member eligibility
   ├── POD validation
   ├── Geographic proximity check
   └── Substation verification
   ↓
4. User links plants to CER
   ↓
5. System creates CER workflows
   ├── CER Constitution
   ├── PNRR Application (if applicable)
   └── Member Onboarding
   ↓
6. System tracks energy sharing
   ↓
7. System generates billing reports
```

### 6.3 Document Management Flow

```
1. Document uploaded (via workflow or directly)
   ↓
2. System analyzes document
   ├── AI extraction (if PDF)
   ├── Portal detection (GSE, Terna, DSO, ADM)
   └── Type classification
   ↓
3. System links document
   ├── To plant (if plant-related)
   ├── To CER (if CER-related)
   ├── To workflow (if workflow-related)
   └── To portal (always)
   ↓
4. System checks expiration (if applicable)
   ↓
5. System creates renewal workflow (if expiring soon)
   ↓
6. Document appears in all relevant contexts
   ├── Plant Documents tab
   ├── Portal Documents filter
   ├── Workflow Documents
   └── Expiring Documents alert
```

---

## 7. Implementation Priorities

> **📋 See ENHANCED_CONSOLIDATION_PLAN.md for detailed feature prioritization (Essential vs Good to Have)**

### Phase 1: Foundation (Months 1-2) - Essential Features Only
**Goal**: Minimum viable product with core functionality

1. ✅ Site hierarchy (Sites → Plants → Assets)
2. ✅ Enhanced plant registry with portal status fields
3. ✅ Basic asset management
4. ✅ Portal integration (GSE, Terna, DSO, ADM)
5. ✅ Document management
6. ✅ Workflow management (multi-phase)
7. ✅ Compliance tracking
8. ✅ Basic asset monitoring
9. ✅ Basic asset maintenance
10. ✅ Authentication & authorization
11. ✅ Basic dashboard

### Phase 2: Operational Excellence (Months 3-4) - P1 Features
**Goal**: Improve operational efficiency and user experience

1. ⭐ Visual plant designer (React Flow canvas)
2. ⭐ String configuration system
3. ⭐ Bulk CSV import for panels
4. ⭐ Asset type-specific fields
5. ⭐ Financial tracking
6. ⭐ Grid exchange / Terna integration
7. ⭐ Weather forecast integration
8. ⭐ Advanced monitoring (thresholds, alerts)
9. ⭐ Advanced maintenance (scheduling, records)

### Phase 3: Advanced Features (Months 5-6) - P1 & P2 Features
**Goal**: Competitive differentiation

1. ⭐ Predictive maintenance
2. ⭐ Advanced analytics & reporting
3. ⭐ CER energy sharing optimization
4. 🔵 Mobile application (MVP)
5. 🔵 QR code / RFID tracking
6. 🔵 Spare parts inventory
7. 🔵 Simulation tools

### Phase 4: Innovation (Months 7-12) - P2 Advanced Features
**Goal**: Industry-leading features

1. 🔵 Digital twin / virtual modeling
2. 🔵 AI document extraction
3. 🔵 IoT / SCADA integration
4. 🔵 ERP integration
5. 🔵 ML / AI features
6. 🔵 Offline mode
7. 🔵 Asset depreciation

---

## 8. Key Architectural Decisions

### 8.1 Visual Plant Designer as Core Feature

**Decision**: Visual plant designer (React Flow canvas) is a first-class feature

**Rationale**:
- Users need to visually design plant architecture
- Component connections define plant topology
- Visual representation improves understanding
- Layout can be auto-generated from assets
- Assets can be created from visual layout

**Implementation**:
- React Flow (@xyflow/react) for canvas
- PlantLayout model for persistence
- Component palette with drag-and-drop
- Real-time energy flow visualization
- Edit/View mode toggle
- Layout sync with Asset model

**Integration Points**:
- Visual Designer → Creates/Updates Assets
- Assets → Auto-generates Visual Layout
- Visual Layout → Used in plant documentation
- Visual Layout → Portal submissions (technical diagrams)

### 8.2 Portal as First-Class Concept

**Decision**: Treat portals (GSE, Terna, DSO, ADM) as first-class entities

**Rationale**:
- Plants interact with multiple portals simultaneously
- Each portal has different requirements, workflows, and documents
- Users think in terms of "GSE status" or "Terna compliance"
- Portal-aware UI improves user experience

**Implementation**:
- Portal status fields in Plant model
- Portal-specific tabs in Plant Detail
- Portal filtering in Document Library
- Portal-aware workflow templates

### 8.2 Document-Plant-CER-Workflow Linking

**Decision**: Documents can link to multiple entities simultaneously

**Rationale**:
- A GSE document belongs to a plant, a workflow, and the GSE portal
- A CER document belongs to a CER, a workflow, and potentially plants
- Documents need to be discoverable from multiple contexts

**Implementation**:
- Multi-foreign-key relationships
- Context-aware document queries
- Portal + entity filtering

### 8.3 Portal Service Abstraction

**Decision**: Create unified PortalService for all portal interactions

**Rationale**:
- Consistent interface for portal operations
- Easier to add new portals
- Centralized portal logic
- Testable portal interactions

**Implementation**:
- PortalService with portal-specific implementations
- PortalType enum
- Portal-specific validations and form generation

---

## 9. UI/UX Principles

### 9.1 Context Switching

**Principle**: Users should easily switch between portal contexts

**Implementation**:
- Tabs within Plant Detail for each portal
- Portal filter in Document Library
- Portal-specific workflow templates
- Portal status indicators throughout UI

### 9.2 Progressive Disclosure

**Principle**: Show overview first, details on demand

**Implementation**:
- Plant Detail → Overview tab shows all portal statuses
- Click portal tab → See portal-specific details
- Click workflow → See workflow details
- Click document → See document details

### 9.3 Workflow Guidance

**Principle**: Guide users through complex portal processes

**Implementation**:
- Multi-phase workflow wizard
- Portal-specific instructions
- Pre-filled forms
- Document checklists
- Deadline tracking

---

## 10. Next Steps

1. **Review this architecture** with stakeholders
2. **Prioritize portal integrations** (start with GSE, Terna)
3. **Design portal-specific UI components**
4. **Implement PortalService** backend abstraction
5. **Enhance Plant Detail** with portal tabs
6. **Integrate CER management** with portal awareness
7. **Consolidate document management** with portal filtering
8. **Build workflow templates** for each portal

---

**Document Status**: Draft for Review  
**Last Updated**: January 2025  
**Next Review**: After stakeholder feedback

