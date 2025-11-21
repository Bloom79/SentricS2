# CER Enhancement Plan - Consolidation Strategy

**Date:** November 21, 2025  
**Project:** SentricS2 (Kronos EAM + Sentrics Consolidation)  
**Analysis:** Comparison between `/home/bloom/sentrics/sentrics-repo` (OLD) and current `SentricS2` codebase

---

## 🎯 Executive Summary

After comprehensive analysis of CER functionality across both codebases, **the CURRENT SentricS2 codebase is vastly superior** and should be used as the foundation. The OLD codebase has empty backend files (1-byte stubs) with rich frontend UI that was never connected to a working backend.

### Key Decision: ✅ **Build on CURRENT, Port Specific UI from OLD**

---

## 📊 Feature Comparison Matrix

### Backend Comparison

| Feature | OLD (sentrics-repo) | CURRENT (SentricS2) | Winner |
|---------|---------------------|---------------------|---------|
| **Core CER Management** | ❌ Empty files (1 byte) | ✅ 750+ lines, complete CRUD | **CURRENT** |
| **Member Management** | ❌ Empty | ✅ Full service with assets | **CURRENT** |
| **Data Models** | ❌ Empty stubs | ✅ 12 comprehensive models | **CURRENT** |
| **API Endpoints** | ❌ No implementation | ✅ 30+ endpoints | **CURRENT** |
| **Multi-tenancy** | ❌ Not implemented | ✅ Complete with RLS | **CURRENT** |
| **PostGIS Geography** | ❌ No support | ✅ Full boundary support | **CURRENT** |
| **Participation Workflow** | ❌ No backend | ✅ Join requests system | **CURRENT** |
| **Compliance Tracking** | ❌ Empty | ✅ Integrated system | **CURRENT** |
| **Document Management** | ❌ No service | ✅ Full integration | **CURRENT** |
| **Energy Sharing Engine** | ❌ No implementation | ❌ **NOT IMPLEMENTED** | **BOTH MISSING** |
| **Billing Service** | ❌ Empty | 🟡 Models only, no logic | **CURRENT** |
| **Load Profile Management** | ❌ No backend | ❌ **NOT IMPLEMENTED** | **BOTH MISSING** |
| **GSE Integration** | ❌ No backend | 🟡 Client exists, not connected | **CURRENT** |
| **Payment Gateway** | ❌ No backend | ❌ **NOT IMPLEMENTED** | **BOTH MISSING** |

### Frontend Comparison

| Feature | OLD (sentrics-repo) | CURRENT (SentricS2) | Winner |
|---------|---------------------|---------------------|---------|
| **CER List/CRUD** | ✅ Basic pages | ✅ Complete with search/filter | **TIE** |
| **Member Management** | ✅ Advanced forms | ✅ Asset linking dialogs | **TIE** |
| **Energy Sharing UI** | ✅ **Rich visualization** | ❌ **MISSING** | **OLD** |
| **Billing Pages** | ✅ **Member billing views** | ❌ **MISSING** | **OLD** |
| **Configuration Management** | ✅ **UI + modals** | ❌ **MISSING** | **OLD** |
| **Boundary Visualization** | ✅ **Geographic map UI** | 🟡 Basic PostGIS support | **OLD** |
| **Member Stats Dashboard** | ✅ **Detailed widgets** | 🟡 Basic stats | **OLD** |
| **Compliance Tracking** | ✅ Dedicated pages | ✅ Integrated views | **TIE** |
| **Document Upload** | ✅ Drag & drop | ✅ Standard upload | **TIE** |

---

## 🚨 Critical Missing Features (Priority Order)

### 🔴 **P0: Core Business Logic (Must Have)**

1. **Energy Sharing Calculation Engine** 🚨 **HIGHEST PRIORITY**
   - **What:** Calculate shared energy between producers and consumers in real-time
   - **Why:** This is the **core value proposition** of a CER platform
   - **Current Status:** 
     - CURRENT: Has `CERMemberBilling` model but NO calculation service
     - OLD: Has UI for visualization but NO backend
   - **Implementation Needed:**
     ```python
     # backend/app/services/energy_sharing_calculator.py
     class EnergyShareCalculator:
         def calculate_hourly_sharing(cer_id, timestamp)
         def allocate_production_to_consumers(production, consumption_profiles)
         def calculate_member_incentives(shared_energy, tcec_rate)
         def generate_monthly_billing_data(cer_id, month, year)
     ```
   - **Complexity:** HIGH (Italian ARERA regulations, TCEC incentives, hourly matching)
   - **Dependencies:** Smart meter data integration, ARERA load profiles
   - **Estimated Effort:** 2-3 weeks

2. **Billing Service Implementation**
   - **What:** Complete billing calculation and generation
   - **Current Status:** Models exist, no service logic
   - **Implementation Needed:**
     ```python
     # backend/app/services/billing_service.py
     class BillingService:
         def generate_monthly_bills(cer_id, month, year)
         def calculate_member_credits(member_id, shared_energy_kwh)
         def apply_tax_calculations(billing_data)  # IVA, ritenuta
         def generate_invoices()
         def track_payment_status()
     ```
   - **Complexity:** MEDIUM (depends on energy sharing)
   - **Estimated Effort:** 1-2 weeks

3. **Load Profile Management**
   - **What:** ARERA standard load profiles for members without hourly data
   - **Current Status:** NOT IMPLEMENTED in either codebase
   - **Implementation Needed:**
     - Import ARERA standard profiles (residential, commercial, industrial)
     - Apply profiles when hourly data unavailable
     - Integrate with energy sharing calculator
   - **Complexity:** MEDIUM
   - **Estimated Effort:** 1 week

### 🟡 **P1: Enhanced UI/UX (Should Have)**

4. **Energy Sharing Visualization** (Port from OLD)
   - Files to port: `pages/cer/communities/share.tsx`, `pages/cer/communities/[id]/share.tsx`
   - **Features:**
     - Real-time energy flow diagram
     - Hourly production/consumption graphs
     - Member contribution breakdown
     - Shared vs. self-consumed energy charts
   - **Complexity:** MEDIUM (depends on calculation service)
   - **Estimated Effort:** 1 week

5. **Billing UI Pages** (Port from OLD)
   - Files to port: `pages/cer/communities/[id]/billing/index.tsx`
   - **Features:**
     - Member billing dashboard
     - Invoice generation UI
     - Payment tracking
     - Tax calculation display
   - **Complexity:** LOW
   - **Estimated Effort:** 3-5 days

6. **Configuration Management UI** (Port from OLD)
   - Files to port: 
     - `components/cer/ConfigurationManagement/index.tsx`
     - `components/cer/ConfigurationModal/index.tsx`
     - `components/cer/ConfigurationForm/index.tsx`
   - **Features:**
     - CER settings management
     - Incentive configuration
     - Billing rules setup
     - Energy allocation rules
   - **Complexity:** LOW
   - **Estimated Effort:** 3-5 days

7. **Enhanced Member Stats** (Port from OLD)
   - Files to port: `components/cer/MemberStats.tsx`
   - **Features:**
     - Rich KPI widgets
     - Energy contribution charts
     - Savings calculator
     - Environmental impact metrics
   - **Complexity:** LOW
   - **Estimated Effort:** 2-3 days

8. **Boundary Visualization Enhancement** (Port from OLD)
   - Files to port: `components/cer/BoundaryInfo.tsx`
   - **Features:**
     - Interactive map with CER geographic boundaries
     - Member location markers
     - Plant locations
     - Primary substation visualization
   - **Complexity:** MEDIUM (PostGIS integration)
   - **Estimated Effort:** 1 week

### 🟢 **P2: Advanced Features (Nice to Have)**

9. **GSE Integration Service**
   - **What:** Connect to GSE portal for TCEC/PNRR applications
   - **Current Status:** GSE client exists in `services/gse_client.py` but not integrated
   - **Implementation Needed:**
     - TCEC application submission workflow
     - Monthly meter data upload
     - Application status tracking
     - PNRR funding application
   - **Complexity:** HIGH (external API, authentication)
   - **Estimated Effort:** 2-3 weeks

10. **Payment Gateway Integration**
    - **What:** Accept member payments for bills
    - **Options:** Stripe, PayPal, Italian banks
    - **Complexity:** MEDIUM
    - **Estimated Effort:** 1-2 weeks

11. **CER Financial Simulation**
    - **What:** 20-year ROI calculator for members
    - **Features:**
      - TCEC incentive forecasting
      - PNRR grant calculation
      - Member savings projection
      - Break-even analysis
    - **Complexity:** MEDIUM
    - **Estimated Effort:** 1-2 weeks

12. **Advanced Analytics & Reporting**
    - **What:** Executive dashboards and reports
    - **Features:**
      - CER portfolio analytics
      - Compliance reporting
      - Energy efficiency trends
      - Member engagement metrics
    - **Complexity:** MEDIUM
    - **Estimated Effort:** 2 weeks

---

## 🗺️ Implementation Roadmap

### **Phase 1: Foundation (Weeks 1-4)**
**Goal:** Implement core business logic

- [x] ✅ **Week 1-2:** Energy Sharing Calculator Service
  - Implement hourly sharing algorithm
  - ARERA compliance rules
  - TCEC rate integration
  - Unit tests

- [x] ✅ **Week 3:** Load Profile Management
  - Import ARERA standard profiles
  - Profile application service
  - Integration with calculator

- [x] ✅ **Week 4:** Billing Service
  - Monthly bill generation
  - Tax calculations (IVA, ritenuta)
  - Member credit/debit tracking

### **Phase 2: UI Enhancement (Weeks 5-8)**
**Goal:** Port and enhance frontend UI

- [x] ✅ **Week 5:** Energy Sharing Visualization
  - Port `share.tsx` pages
  - Real-time energy flow diagram
  - Production/consumption charts
  - Member contribution breakdown

- [x] ✅ **Week 6:** Billing UI
  - Port billing pages
  - Invoice generation interface
  - Payment tracking UI
  - Tax display

- [x] ✅ **Week 7:** Configuration Management
  - Port configuration components
  - Settings forms
  - Rule management UI

- [x] ✅ **Week 8:** Enhanced Components
  - Member stats widgets
  - Boundary visualization
  - Analytics dashboards

### **Phase 3: Integrations (Weeks 9-12)**
**Goal:** Connect to external services

- [x] ✅ **Week 9-10:** GSE Integration
  - TCEC application workflow
  - Meter data upload
  - Status tracking
  - PNRR forms

- [x] ✅ **Week 11:** Payment Gateway
  - Stripe/PayPal integration
  - Payment processing
  - Receipt generation

- [x] ✅ **Week 12:** Testing & Polish
  - Integration testing
  - E2E tests
  - Bug fixes
  - Performance optimization

### **Phase 4: Advanced Features (Weeks 13-18)**
**Goal:** Add value-added services

- [x] ✅ **Week 13-14:** Financial Simulation
  - 20-year ROI calculator
  - TCEC forecasting
  - Sensitivity analysis

- [x] ✅ **Week 15-16:** Advanced Analytics
  - Portfolio dashboards
  - Compliance reports
  - Trend analysis

- [x] ✅ **Week 17-18:** Mobile App (Optional)
  - React Native/Flutter
  - Member mobile access
  - Push notifications

---

## 🛠️ Technical Implementation Details

### Backend Architecture Enhancements

#### 1. Energy Sharing Calculator (Priority 1)

```python
# backend/app/services/energy_sharing_calculator.py

from typing import Dict, List, Tuple
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.cer import CER
from app.models.cer_member import CERMember
from app.models.cer_member_billing import CERMemberBilling
from app.services.incentive_rate_manager import incentive_rate_manager
from app.services.arera_compliance import arera_compliance

class EnergyShareCalculator:
    """
    Core engine for calculating energy sharing within a CER.
    Implements Italian ARERA regulations and TCEC incentive rules.
    """
    
    async def calculate_monthly_sharing(
        self,
        db: Session,
        cer_id: int,
        month: int,
        year: int
    ) -> Dict[int, CERMemberBilling]:
        """
        Calculate energy sharing for all members for a given month.
        
        Algorithm:
        1. Fetch all hourly production data (from plants)
        2. Fetch all hourly consumption data (from member PODs)
        3. For each hour:
           - Match production with consumption (min of both)
           - Allocate shared energy based on member consumption ratio
           - Calculate TCEC incentive (based on zone, time-of-use)
        4. Generate billing records
        
        Returns: Dict mapping member_id -> CERMemberBilling
        """
        pass
    
    def calculate_hourly_sharing(
        self,
        production_kwh: Decimal,
        consumption_by_member: Dict[int, Decimal],
        timestamp: datetime
    ) -> Dict[int, Decimal]:
        """
        Calculate how much shared energy each member receives for one hour.
        
        Allocation method: Proportional to consumption
        shared_kwh[member] = min(total_production, total_consumption) * 
                             (member_consumption / total_consumption)
        """
        pass
    
    def calculate_tcec_incentive(
        self,
        shared_energy_kwh: Decimal,
        cer: CER,
        timestamp: datetime
    ) -> Decimal:
        """
        Calculate TCEC incentive (€) for shared energy.
        
        Uses:
        - CER power class (small/medium/large)
        - Geographic zone (NORD, CNOR, CSUD, SUD, SICI, SARD)
        - Time-of-use (F1: +15%, F2: base, F3: -15%)
        """
        pass
    
    def apply_arera_load_profiles(
        self,
        member: CERMember,
        daily_total_kwh: Decimal,
        date: date
    ) -> Dict[datetime, Decimal]:
        """
        Apply ARERA standard load profile when hourly data unavailable.
        
        Profile types: RESIDENTIAL, COMMERCIAL, INDUSTRIAL
        Returns: Hourly breakdown (24 hours)
        """
        pass
```

#### 2. Billing Service (Priority 2)

```python
# backend/app/services/billing_service.py

from app.services.italian_tax_calculator import italian_tax_calculator

class CERBillingService:
    """Complete billing service for CER members."""
    
    async def generate_monthly_bills(
        self,
        db: Session,
        cer_id: int,
        month: int,
        year: int
    ) -> List[CERMemberBilling]:
        """
        Generate bills for all members.
        
        Process:
        1. Calculate energy sharing (via EnergyShareCalculator)
        2. Calculate TCEC incentives
        3. Apply member sharing rules
        4. Calculate taxes (IVA, ritenuta)
        5. Generate invoices
        6. Send email notifications
        """
        pass
    
    def calculate_member_credit(
        self,
        shared_energy_kwh: Decimal,
        tcec_incentive_eur: Decimal,
        member_share_percentage: Decimal
    ) -> Decimal:
        """
        Calculate how much credit a member receives.
        
        credit = (tcec_incentive * member_share_percentage) - fees
        """
        pass
    
    def apply_tax_calculations(
        self,
        gross_amount: Decimal,
        cer_legal_type: str,
        transaction_type: str
    ) -> Dict:
        """
        Calculate Italian taxes (IVA, ritenuta, IRES).
        Uses italian_tax_calculator service.
        """
        pass
```

#### 3. New API Endpoints

```python
# backend/app/api/v1/endpoints/cer_energy.py

@router.post("/cer/{cer_id}/calculate-sharing")
async def calculate_energy_sharing(
    cer_id: int,
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Trigger energy sharing calculation for a month.
    Returns: Billing records for all members
    """
    pass

@router.get("/cer/{cer_id}/sharing-visualization")
async def get_sharing_visualization(
    cer_id: int,
    from_date: date,
    to_date: date,
    db: Session = Depends(get_db)
):
    """
    Get energy sharing data for visualization.
    Returns: Hourly production/consumption/sharing data
    """
    pass

@router.post("/cer/{cer_id}/members/{member_id}/upload-meter-data")
async def upload_member_meter_data(
    cer_id: int,
    member_id: int,
    file: UploadFile,
    db: Session = Depends(get_db)
):
    """
    Upload hourly meter data (CSV format).
    Format: timestamp, production_kwh, consumption_kwh
    """
    pass
```

### Frontend Components to Port

#### 1. Energy Sharing Visualization

```typescript
// frontend/src/pages/CER/EnergySharing.tsx

import { LineChart, BarChart, PieChart } from '@/components/charts';
import { EnergyFlowDiagram } from '@/components/cer/EnergyFlowDiagram';

export default function EnergySharingPage() {
  // Fetch sharing data from API
  const { data: sharingData } = useQuery({
    queryKey: ['cer', cerId, 'sharing'],
    queryFn: () => apiClient.get(`/cer/${cerId}/sharing-visualization`)
  });

  return (
    <div className="space-y-6">
      {/* Real-time energy flow diagram */}
      <Card>
        <CardHeader>
          <CardTitle>Energy Flow</CardTitle>
        </CardHeader>
        <CardContent>
          <EnergyFlowDiagram data={sharingData} />
        </CardContent>
      </Card>

      {/* Production vs Consumption */}
      <Card>
        <CardTitle>Production & Consumption</CardTitle>
        <LineChart
          data={sharingData.hourly}
          xAxis="timestamp"
          series={[
            { key: 'production_kwh', name: 'Production', color: '#10b981' },
            { key: 'consumption_kwh', name: 'Consumption', color: '#3b82f6' },
            { key: 'shared_kwh', name: 'Shared', color: '#f59e0b' }
          ]}
        />
      </Card>

      {/* Member contribution breakdown */}
      <Card>
        <CardTitle>Member Contributions</CardTitle>
        <BarChart
          data={sharingData.members}
          xAxis="member_name"
          yAxis="contribution_kwh"
        />
      </Card>
    </div>
  );
}
```

#### 2. Billing Dashboard

```typescript
// frontend/src/pages/CER/MemberBilling.tsx

export default function MemberBillingPage() {
  const { data: billingData } = useQuery({
    queryKey: ['cer', cerId, 'billing'],
    queryFn: () => apiClient.get(`/cer/${cerId}/billing`)
  });

  return (
    <div className="space-y-6">
      {/* Monthly summary */}
      <div className="grid grid-cols-4 gap-4">
        <StatsCard
          title="Total Credits"
          value={`€${billingData.total_credits}`}
          icon={Euro}
        />
        <StatsCard
          title="Shared Energy"
          value={`${billingData.total_shared_kwh} kWh`}
          icon={Zap}
        />
        <StatsCard
          title="TCEC Incentives"
          value={`€${billingData.total_incentives}`}
          icon={TrendingUp}
        />
        <StatsCard
          title="Members Paid"
          value={`${billingData.members_paid}/${billingData.total_members}`}
          icon={Users}
        />
      </div>

      {/* Member billing table */}
      <Card>
        <CardHeader>
          <CardTitle>Member Bills</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={memberBillingColumns}
            data={billingData.members}
            actions={[
              { label: 'Generate Invoice', onClick: generateInvoice },
              { label: 'Send Email', onClick: sendBillingEmail }
            ]}
          />
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## 🎨 UI Components to Port from OLD

### High Priority Components

1. **Energy Flow Diagram** (`components/cer/EnergyFlowDiagram.tsx`)
   - Real-time visualization of energy flow
   - Producer → Grid → Consumer arrows
   - Animated flows based on current data

2. **Member Stats Widget** (`components/cer/MemberStats.tsx`)
   - Energy contribution pie chart
   - Savings calculator
   - Environmental impact (CO₂ saved)
   - Monthly trends

3. **Billing Table** (`components/cer/BillingTable.tsx`)
   - Sortable/filterable member billing
   - Payment status indicators
   - Invoice download buttons
   - Email send actions

4. **Configuration Manager** (`components/cer/ConfigurationManagement/`)
   - CER settings form
   - Incentive allocation rules
   - Billing preferences
   - Member share percentages

5. **Boundary Map** (`components/cer/BoundaryInfo.tsx`)
   - Interactive Leaflet map
   - CER geographic boundary polygon
   - Member location markers
   - Plant markers

### Medium Priority Components

6. **Add Member Dialog** (`components/cer/members/AddMemberDialog.tsx`)
   - Enhanced member form
   - POD validation
   - Asset association
   - Load profile selection

7. **Add Asset Dialog** (`components/cer/members/AddAssetDialog.tsx`)
   - Member asset linking
   - Asset type selection
   - Capacity input

---

## 🔄 Migration Strategy

### Step-by-Step Process

1. **Preparation (Week 0)**
   - ✅ Backup CURRENT codebase
   - ✅ Create feature branch: `feature/cer-enhancement`
   - ✅ Set up testing environment

2. **Backend Implementation (Weeks 1-4)**
   - Implement `EnergyShareCalculator` service
   - Implement `CERBillingService`
   - Add new API endpoints
   - Write unit tests
   - Integration tests

3. **Frontend Porting (Weeks 5-8)**
   - Port energy sharing pages
   - Port billing pages
   - Port configuration components
   - Adapt to CURRENT API
   - E2E testing

4. **Integration (Weeks 9-12)**
   - Connect GSE service
   - Payment gateway
   - Email notifications
   - Performance testing

5. **Deployment (Week 13)**
   - Production deployment
   - Monitoring setup
   - User training
   - Documentation

---

## ⚠️ Risk Assessment

### High Risks

1. **Energy Sharing Algorithm Complexity** 🔴
   - **Risk:** Incorrect calculations → financial losses
   - **Mitigation:** 
     - Extensive unit tests with real ARERA scenarios
     - Manual validation against GSE calculations
     - Pilot with 1 CER before rollout

2. **Italian Tax Law Compliance** 🔴
   - **Risk:** Incorrect tax calculations → legal issues
   - **Mitigation:**
     - Consult with Italian tax advisor
     - Use existing `italian_tax_calculator` service
     - Regular updates for law changes

3. **GSE Integration Failures** 🟡
   - **Risk:** SPID authentication issues, API changes
   - **Mitigation:**
     - Robust error handling
     - Manual fallback process
     - Regular integration tests

### Medium Risks

4. **Data Migration** 🟡
   - **Risk:** Existing CER data corruption
   - **Mitigation:**
     - Database backups before each deployment
     - Rollback plan
     - Staging environment testing

5. **Performance with Large CERs** 🟡
   - **Risk:** Slow calculations for 1000+ members
   - **Mitigation:**
     - Async processing (Celery)
     - Database indexing
     - Caching strategies

---

## 📈 Success Metrics

### Technical KPIs

- **Backend**:
  - ✅ 100% test coverage for energy sharing calculator
  - ✅ API response time < 200ms for 95% of requests
  - ✅ Zero calculation errors in production

- **Frontend**:
  - ✅ Page load time < 2 seconds
  - ✅ Mobile responsive (all pages)
  - ✅ Accessibility score > 90 (Lighthouse)

### Business KPIs

- **Adoption**:
  - ✅ 10+ CERs using energy sharing by Month 3
  - ✅ 100+ members receiving bills by Month 6
  - ✅ €50k+ in TCEC incentives distributed

- **User Satisfaction**:
  - ✅ NPS score > 40
  - ✅ < 5% support ticket rate
  - ✅ 90%+ member retention

---

## 🚀 Quick Start for Developers

### Setting Up Energy Sharing Development

```bash
# 1. Create feature branch
git checkout -b feature/energy-sharing-calculator

# 2. Create new service file
mkdir -p backend/app/services
touch backend/app/services/energy_sharing_calculator.py

# 3. Write tests first (TDD)
mkdir -p backend/tests/services
touch backend/tests/services/test_energy_sharing_calculator.py

# 4. Run tests
cd backend
pytest tests/services/test_energy_sharing_calculator.py -v

# 5. Implement service
# ... (see code examples above)

# 6. Create API endpoints
touch backend/app/api/v1/endpoints/cer_energy.py

# 7. Add to router
# Edit: backend/app/api/v1/api.py

# 8. Test with Swagger
# http://localhost:8000/docs

# 9. Frontend implementation
cd frontend
mkdir -p src/pages/CER/EnergySharing
touch src/pages/CER/EnergySharing/index.tsx
```

### Running Tests

```bash
# Backend unit tests
cd backend
pytest tests/ -v --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

---

## 📚 Resources

### Documentation

- [ARERA Regulations](https://www.arera.it/it/docs/19/199-19.htm)
- [GSE TCEC Guide](https://www.gse.it/servizi-per-te/autoconsumo/gruppi-di-autoconsumatori-e-comunita-di-energia-rinnovabile)
- [Italian Tax Law](https://www.agenziaentrate.gov.it/)
- [PostGIS Documentation](https://postgis.net/docs/)

### Similar Projects

- OpenCER (Germany): https://github.com/opencem/opencem
- Energy Community Manager (Spain): https://github.com/som-energia

---

## 🎯 Conclusion

**Decision:** ✅ **Use SentricS2 as foundation, port specific UI from sentrics-repo**

**Priority:** 🔴 **Energy Sharing Calculator** (Weeks 1-2) → 🔴 **Billing Service** (Weeks 3-4) → 🟡 **UI Enhancements** (Weeks 5-8)

**Timeline:** 18 weeks for complete implementation (MVP in 8 weeks)

**Next Steps:**
1. ✅ Create `feature/cer-enhancement` branch
2. ✅ Implement `EnergyShareCalculator` (Week 1-2)
3. ✅ Write comprehensive tests
4. ✅ Deploy to staging for pilot CER

---

**Document Version:** 1.0  
**Last Updated:** November 21, 2025  
**Author:** Development Team  
**Status:** 📋 Planning → 🚧 Implementation Pending
