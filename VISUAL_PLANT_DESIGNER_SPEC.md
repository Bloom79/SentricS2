# Visual Plant Designer Specification

## Overview

The Visual Plant Designer is a drag-and-drop canvas interface for designing renewable energy plant architectures. Users can visually place components (solar panels, inverters, batteries, etc.) and connect them to define the plant's energy flow topology.

## Technology Stack

- **Library**: React Flow (@xyflow/react) v12.4.2+
- **Backend Storage**: PostgreSQL JSON columns for nodes/edges
- **Integration**: Linked to Asset model for persistence

## Component Architecture

### Frontend Components

```
PlantVisualDesigner/
├── FlowCanvas.tsx (Main canvas container)
├── ComponentsPalette.tsx (Drag-and-drop component library)
├── FlowNodeTypes.tsx (Node type registry)
├── FlowNodes/
│   ├── SolarPanelNode.tsx
│   ├── SolarArrayNode.tsx
│   ├── WindTurbineNode.tsx
│   ├── WindTurbineClusterNode.tsx
│   ├── InverterNode.tsx
│   ├── TransformerNode.tsx
│   ├── CollectorSubstationNode.tsx
│   ├── BESSNode.tsx
│   ├── GridNode.tsx
│   ├── ConsumerNode.tsx
│   ├── SCADANode.tsx
│   └── SensorNode.tsx
├── NodeDetailsSidebar.tsx (Component properties editor)
├── EdgeDialog.tsx (Connection properties)
└── FlowControls.tsx (Zoom, pan, fit view controls)
```

### Component Categories

#### 1. Generation Components
- **Solar Array**: Large-scale solar installation
- **Solar Panel**: Individual panel component
- **Wind Turbine**: Individual wind turbine
- **Wind Turbine Cluster**: Group of turbines

#### 2. Power Conversion Components
- **Inverter**: DC to AC conversion
- **Transformer**: Voltage transformation
- **Collector Substation**: Power collection point

#### 3. Storage Components
- **BESS (Battery Energy Storage System)**: Battery storage

#### 4. Consumption Components
- **Consumer**: Energy consumption point (Residential, Industrial, Commercial)

#### 5. Grid Components
- **Grid**: Power grid connection point

#### 6. Monitoring Components
- **SCADA System**: Supervisory control and data acquisition
- **Sensor**: Monitoring sensor

## Data Model

### PlantLayout Model

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
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    plant = relationship("Plant", back_populates="layout")
```

### Node Structure (React Flow)

```typescript
interface FlowNode {
  id: string;  // Asset instance ID or generated ID
  type: FlowNodeType;  // 'solar panel', 'inverter', etc.
  position: { x: number; y: number };
  data: {
    id: string;
    label: string;
    type: FlowNodeType;
    specs: {
      power?: number;
      efficiency?: number;
      [key: string]: any;  // Type-specific attributes
    };
    status: 'active' | 'inactive' | 'error';
  };
  draggable: boolean;
  connectable: boolean;
}
```

### Edge Structure (React Flow)

```typescript
interface FlowEdge {
  id: string;
  source: string;  // Source node ID
  target: string;  // Target node ID
  sourceHandle?: string;
  targetHandle?: string;
  type?: string;
  animated?: boolean;
  data?: {
    energyFlow?: number;
    efficiency?: number;
    losses?: number[];
  };
}
```

## User Workflows

### 1. Creating a Plant Layout

1. User opens Plant Detail → Visual Designer tab
2. System loads existing layout (if exists) or shows empty canvas
3. User switches to Edit Mode
4. User drags components from palette onto canvas
5. System prompts for component properties (or uses existing asset)
6. User connects components by dragging from source to target
7. System validates connection (checks valid connection types)
8. User saves layout → System persists to database

### 2. Editing Existing Layout

1. User opens Plant Detail → Visual Designer tab
2. System loads saved layout
3. User switches to Edit Mode
4. User can:
   - Drag existing components to reposition
   - Delete components (removes from canvas, optionally deletes asset)
   - Add new components
   - Modify connections
   - Edit component properties
5. User saves changes → System updates database

### 3. Viewing Layout (Read-only)

1. User opens Plant Detail → Visual Designer tab
2. System loads saved layout
3. View Mode active (no editing)
4. User can:
   - Pan and zoom
   - Click components to view details
   - See real-time energy flow (if data available)
   - View component status

## API Endpoints

### Plant Layout Endpoints

```python
# Save plant layout
POST /api/v1/plants/{plant_id}/layout
Body: {
  "nodes": [...],
  "edges": [...]
}

# Load plant layout
GET /api/v1/plants/{plant_id}/layout

# Delete plant layout
DELETE /api/v1/plants/{plant_id}/layout

# Generate layout from assets
POST /api/v1/plants/{plant_id}/layout/generate-from-assets
```

## Integration with Asset Model

### Synchronization Strategy

**Option 1: Layout → Assets (One-way)**
- Visual layout creates/updates assets
- Assets can be edited independently
- Layout regeneration overwrites asset positions

**Option 2: Assets → Layout (One-way)**
- Assets define plant structure
- Layout auto-generated from assets
- Layout is read-only visualization

**Option 3: Bidirectional Sync (Recommended)**
- Layout changes update assets
- Asset changes update layout
- Conflict resolution needed

**Recommended**: Option 3 with manual sync trigger

### Asset Creation from Layout

When user drops component on canvas:
1. Check if asset instance exists (by ID)
2. If exists: Use existing asset
3. If not: Create new asset instance
4. Link asset to plant
5. Store asset ID in node.id

### Layout Generation from Assets

When user clicks "Generate Layout":
1. Fetch all assets for plant
2. Create nodes from assets
3. Auto-position nodes (grid layout)
4. Generate edges based on asset relationships
5. Save layout

## Validation Rules

### Connection Validation

```typescript
const VALID_CONNECTIONS = {
  'solar array': ['inverter', 'transformer'],
  'solar panel': ['inverter', 'transformer'],
  'wind turbine': ['inverter', 'transformer'],
  'battery': ['inverter', 'transformer', 'grid', 'consumer'],
  'bess': ['inverter', 'transformer', 'grid', 'consumer'],
  'inverter': ['transformer', 'grid', 'consumer', 'battery', 'bess'],
  'transformer': ['grid', 'consumer', 'battery', 'bess'],
  'grid': ['consumer', 'battery', 'bess'],
  'consumer': [],
  'sensor': ['*'],  // Can connect to any
  'scada system': ['*']  // Can connect to any
};
```

### Power Flow Validation

- Total generation capacity ≥ Total consumption
- Inverter capacity ≥ Connected generation
- Transformer capacity ≥ Inverter output
- Grid capacity ≥ Plant output

## Real-time Features

### Energy Flow Visualization

- Animated edges showing energy flow direction
- Color-coded by flow magnitude
- Fault indicators (red edges for issues)
- Efficiency metrics displayed on edges

### Component Status

- Visual indicators for component status
- Green: Operational
- Yellow: Warning
- Red: Error/Offline
- Gray: Inactive

## Dependencies

### Frontend Dependencies

```json
{
  "@xyflow/react": "^12.4.2"
}
```

### Backend Dependencies

- Existing: PostgreSQL with JSON support
- No additional dependencies needed

## Migration from Sentrics

### Files to Migrate

1. **Components**:
   - `FlowCanvas.tsx`
   - `ComponentsPalette.tsx`
   - `FlowNodeTypes.tsx`
   - All `FlowNodes/*.tsx` files
   - `NodeDetailsSidebar.tsx`
   - `EdgeDialog.tsx`
   - `FlowControls.tsx`

2. **Utilities**:
   - `initialFlowTemplate.ts`
   - `flowLayout.ts`
   - `flowEdgeConfig.ts`

3. **Types**:
   - `flowComponents.ts`

4. **Hooks**:
   - `useFlowData.ts` (if exists)

### Adaptations Needed

1. **Replace Supabase**:
   - Replace `supabase.from('energy_flows')` with API calls
   - Update to use `apiClient` from consolidated project

2. **Asset Service Integration**:
   - Replace `assetService` calls with consolidated API
   - Update to use multi-tenant asset service

3. **Plant Model**:
   - Link layout to Plant model
   - Add `layout` relationship

4. **Styling**:
   - Ensure consistent with consolidated UI theme
   - Use consolidated UI components (Card, Button, etc.)

## Implementation Checklist

### Backend
- [ ] Create `PlantLayout` model
- [ ] Create `plant_layout_service.py`
- [ ] Create API endpoints for layout CRUD
- [ ] Add layout relationship to Plant model
- [ ] Create migration for `plant_layouts` table

### Frontend
- [ ] Install `@xyflow/react` dependency
- [ ] Migrate FlowCanvas component
- [ ] Migrate ComponentsPalette component
- [ ] Migrate all FlowNode components
- [ ] Migrate utility functions
- [ ] Replace Supabase calls with API calls
- [ ] Integrate into Plant Detail page
- [ ] Add Visual Designer tab
- [ ] Test drag-and-drop functionality
- [ ] Test save/load functionality
- [ ] Test connection validation
- [ ] Test asset synchronization

### Integration
- [ ] Link layout to Asset model
- [ ] Implement layout → asset sync
- [ ] Implement asset → layout generation
- [ ] Test bidirectional sync
- [ ] Add validation rules
- [ ] Add power flow validation

---

**Status**: Specification Complete  
**Priority**: HIGH - Critical feature from Sentrics  
**Estimated Effort**: 3-4 weeks  
**Dependencies**: @xyflow/react, Asset model integration


