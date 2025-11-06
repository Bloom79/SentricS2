# Phase 1: BESS Basic Monitoring - Technical Specification

## Executive Summary

Battery Energy Storage Systems (BESS) represent Italy's fastest-growing energy market segment, with the MACSE (Meccanismo di Approvvigionamento di Capacità di Stoccaggio Elettrico) auction on September 30, 2025 offering 10 GWh of capacity contracts at starting prices of €37,000/MWh/year over 15-year terms.

This specification defines a **BESS Basic Monitoring Module** for SentricS2 that provides:

1. **Real-time SOC (State of Charge) monitoring** - Mandatory for grid services
2. **Performance tracking** - Efficiency, cycle counting, degradation analysis
3. **MACSE compliance** - Documentation and reporting for auction participation
4. **Revenue optimization** - Integration with 15-minute trading for arbitrage opportunities
5. **Multi-vendor support** - Standardized interfaces for Tesla, BYD, Huawei, Sungrow, etc.

**Market Context:**
- **Italy leads Europe in BESS growth:** 71 GWh needed by 2030
- **MACSE auction imminent:** September 30, 2025 - first major capacity mechanism
- **EU investment:** €17.7B allocated to battery storage 2024-2030
- **TIDE integration:** 15-minute settlement creates arbitrage opportunities
- **Revenue streams:** Capacity payments (€37k/MWh/year) + energy arbitrage + grid services

**Phase 1 Scope (Q2-Q3 2025):**
- Basic SOC/SOH monitoring
- Performance metrics (efficiency, cycles, degradation)
- MACSE documentation preparation
- Manual SCADA data import
- Basic arbitrage opportunity alerts

**Future Phases:**
- Phase 2: Real-time SCADA integration, automated bidding
- Phase 3: AI-powered degradation prediction, VPP aggregation
- Phase 4: Advanced ancillary services (FCR, aFRR, mFRR)

---

## 1. Market Opportunity Analysis

### 1.1 MACSE Auction Details

**First Auction: September 30, 2025**

| Parameter | Value |
|-----------|-------|
| **Capacity Offered** | 10 GWh |
| **Contract Duration** | 15 years |
| **Starting Price** | €37,000/MWh/year |
| **Payment Structure** | Availability-based (80% min availability required) |
| **Technical Requirements** | 4-hour discharge duration, round-trip efficiency ≥85% |
| **Minimum Bid Size** | 1 MW / 4 MWh |
| **Delivery Start** | January 1, 2026 |

**Revenue Calculation Example:**
```
10 MW / 40 MWh battery:
- Capacity payment: 40 MWh × €37,000/MWh = €1,480,000/year
- Energy arbitrage: ~€200,000/year (conservative, TIDE-based)
- Grid services: ~€100,000/year (FCR-D, aFRR)
- Total: €1,780,000/year for 15 years

15-year NPV (8% discount): €15.2M
CAPEX: ~€8M (€200/kWh)
IRR: ~18%
```

### 1.2 Technical Requirements (Terna Document A.79)

**Terna's Grid Connection Requirements for BESS:**

1. **State of Charge (SOC) Monitoring**
   - Real-time SOC reporting to Terna TSO
   - 1-minute granularity minimum
   - Accuracy: ±2% of nominal capacity
   - Available SOC range: 10%-90% for grid services (80% DoD max)

2. **Round-Trip Efficiency**
   - Minimum: 85% (AC-AC)
   - Measured: (Energy discharged / Energy charged) × 100
   - Excludes auxiliary consumption
   - Monthly reporting required

3. **Response Time**
   - Frequency Containment Reserve (FCR): <2 seconds
   - Automatic Frequency Restoration Reserve (aFRR): <5 seconds
   - Manual Frequency Restoration Reserve (mFRR): <15 minutes

4. **Cycle Life Tracking**
   - Expected: ~365 full cycles/year (1 cycle/day)
   - MACSE contract allows up to 400 cycles/year
   - Half-cycle tracking (charge or discharge separately)
   - Weighted by depth of discharge (DoD)

5. **SCADA Integration**
   - IEC 61850 or IEC 60870-5-104 protocol
   - Real-time data transmission to Terna
   - Historical data retention: 10 years
   - Cybersecurity: IEC 62351 compliance

### 1.3 Market Sizing

**Italy BESS Market 2025-2030:**

| Year | Installed Capacity | New Installations | Market Value | SentricS2 Target |
|------|-------------------|-------------------|--------------|------------------|
| 2025 | 3.2 GWh | 1.5 GWh | €300M | 50 MWh (€1M) |
| 2026 | 8.5 GWh | 5.3 GWh | €1.1B | 500 MWh (€10M) |
| 2027 | 18 GWh | 9.5 GWh | €1.9B | 2 GWh (€40M) |
| 2028 | 32 GWh | 14 GWh | €2.8B | 5 GWh (€100M) |
| 2030 | 71 GWh | ~20 GWh/year | €4B | 10 GWh (€200M) |

**Target Customers:**
1. **MACSE Auction Participants:** 20-30 operators bidding for 10 GWh (Sep 2025)
2. **Utility-Scale BESS:** 50+ MW/200+ MWh projects (5-10 in Italy by 2026)
3. **Commercial & Industrial:** 500 kW - 5 MW behind-the-meter storage
4. **Renewable + Storage:** 1,500+ solar farms adding co-located batteries
5. **VPP Aggregators:** Pooling distributed BESS for grid services

**Revenue Model:**
- **MACSE Documentation Service:** €5,000-€15,000 per application (one-time)
- **Monitoring SaaS:** €200-€500/MWh/month (€2,400-€6,000/MWh/year)
- **Optimization Suite:** €500-€1,000/MWh/month (includes 15-min trading integration)
- **SCADA Integration:** €10,000-€50,000 per site (one-time)

**Example Customer:**
- 10 MW / 40 MWh utility-scale BESS
- MACSE documentation: €10,000
- Monitoring: €500/MWh × 40 MWh = €20,000/month = €240,000/year
- Optimization: €1,000/MWh × 40 MWh = €40,000/month = €480,000/year
- **Total Annual Revenue:** €720,000

---

## 2. System Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SentricS2 Platform                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          BESS Monitoring Dashboard                      │ │
│  │  • Real-time SOC/SOH display                           │ │
│  │  • Performance metrics                                 │ │
│  │  • Arbitrage opportunity alerts                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────┼────────────────────────────────┐ │
│  │                API Layer                                 │ │
│  │  /api/v1/bess/assets                                    │ │
│  │  /api/v1/bess/telemetry                                 │ │
│  │  /api/v1/bess/performance                               │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────┼────────────────────────────────┐ │
│  │              Service Layer                               │ │
│  │  • BESSAssetService                                     │ │
│  │  • BESSTelemetryService                                 │ │
│  │  • BESSPerformanceService                               │ │
│  │  • ArbitrageOpportunityService                          │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────┼────────────────────────────────┐ │
│  │         Database (PostgreSQL)                            │ │
│  │  • bess_assets                                          │ │
│  │  • bess_telemetry                                       │ │
│  │  • bess_performance_metrics                             │ │
│  │  • bess_cycles                                          │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────────┐      ┌───────────┐      ┌──────────┐
   │ Manual │      │  SCADA    │      │ Vendor   │
   │ Import │      │ Gateway   │      │ Cloud    │
   │ (CSV)  │      │ (Phase 2) │      │ API      │
   └────────┘      └───────────┘      └──────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                  ┌─────────────────┐
                  │  BESS Hardware  │
                  │                 │
                  │  Tesla          │
                  │  BYD            │
                  │  Huawei         │
                  │  Sungrow        │
                  │  Fluence        │
                  └─────────────────┘
```

### 2.2 Data Flow

**Phase 1A: Manual Import (Weeks 1-4)**
```
1. BESS operator exports telemetry from vendor system
   ↓
2. Upload CSV/Excel to SentricS2
   ↓
3. Validation & parsing (SOC, voltage, current, temperature)
   ↓
4. Store in bess_telemetry table
   ↓
5. Calculate performance metrics (efficiency, cycles)
   ↓
6. Display in dashboard with alerts
```

**Phase 1B: Vendor API Integration (Weeks 5-8)**
```
1. Configure vendor API credentials (Tesla Cloud, BYD BMS, etc.)
   ↓
2. Scheduled polling (1-minute intervals)
   ↓
3. Parse vendor-specific JSON/XML format
   ↓
4. Normalize to standard schema
   ↓
5. Real-time updates to dashboard
```

**Phase 2: SCADA Integration (Q4 2025)**
```
1. IEC 61850 / Modbus TCP connection
   ↓
2. Real-time telemetry stream
   ↓
3. Process & store high-frequency data (1-second intervals)
   ↓
4. Integration with Terna TSO reporting
```

### 2.3 Vendor Support Matrix

| Vendor | Market Share (Italy) | API Available | SCADA Protocol | Phase 1 Support |
|--------|---------------------|---------------|----------------|-----------------|
| **Tesla Megapack** | 35% | Yes (Cloud API) | IEC 61850 | ✅ API + Manual |
| **BYD Battery-Box** | 25% | Yes (BMS API) | Modbus TCP | ✅ API + Manual |
| **Huawei LUNA** | 15% | Yes (FusionSolar) | IEC 60870-5-104 | ✅ API + Manual |
| **Sungrow PowerTitan** | 10% | Limited | IEC 61850 | ⚠️ Manual only |
| **Fluence Gridstack** | 8% | Yes (Mosaic) | IEC 61850 | ✅ API + Manual |
| **Others** | 7% | Varies | Varies | ⚠️ Manual + custom |

---

## 3. Technical Implementation

### 3.1 Database Schema

```sql
-- BESS Asset Registry
CREATE TABLE bess_assets (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR NOT NULL,
    site_id INTEGER REFERENCES sites(id),

    -- Basic Info
    name VARCHAR(200) NOT NULL,
    manufacturer VARCHAR(100),  -- 'Tesla', 'BYD', 'Huawei', etc.
    model VARCHAR(100),
    serial_number VARCHAR(100),

    -- Capacity Specifications
    nominal_capacity_kwh DECIMAL(10,2) NOT NULL,
    usable_capacity_kwh DECIMAL(10,2),  -- Accounting for DoD limits
    nominal_power_kw DECIMAL(10,2) NOT NULL,
    max_charge_rate_kw DECIMAL(10,2),
    max_discharge_rate_kw DECIMAL(10,2),

    -- Technical Specs
    chemistry VARCHAR(50),  -- 'LFP', 'NMC', 'NCA', 'LTO'
    voltage_nominal_v DECIMAL(8,2),
    voltage_min_v DECIMAL(8,2),
    voltage_max_v DECIMAL(8,2),
    round_trip_efficiency_pct DECIMAL(5,2),  -- Rated efficiency

    -- Operational Limits
    soc_min_pct DECIMAL(5,2) DEFAULT 10.0,  -- Minimum SOC (typically 10%)
    soc_max_pct DECIMAL(5,2) DEFAULT 90.0,  -- Maximum SOC (typically 90%)
    depth_of_discharge_max_pct DECIMAL(5,2) DEFAULT 80.0,  -- Max DoD for longevity

    -- Lifecycle Info
    installation_date DATE,
    warranty_cycles INTEGER,  -- e.g., 6000 cycles
    warranty_years INTEGER,   -- e.g., 10 years
    expected_eol_date DATE,   -- End of life estimate

    -- MACSE Participation
    macse_eligible BOOLEAN DEFAULT false,
    macse_application_date DATE,
    macse_contract_id VARCHAR(100),
    macse_capacity_awarded_mwh DECIMAL(10,2),

    -- Data Integration
    data_source VARCHAR(50),  -- 'manual', 'api', 'scada'
    vendor_api_endpoint VARCHAR(500),
    vendor_api_credentials_encrypted TEXT,
    scada_protocol VARCHAR(50),  -- 'IEC61850', 'ModbusTCP', 'IEC60870'
    scada_ip_address VARCHAR(50),
    polling_interval_seconds INTEGER DEFAULT 60,

    -- Status
    operational_status VARCHAR(50),  -- 'operational', 'maintenance', 'degraded', 'offline'
    is_active BOOLEAN DEFAULT true,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Indexes
    INDEX idx_bess_assets_tenant (tenant_id),
    INDEX idx_bess_assets_site (site_id),
    INDEX idx_bess_assets_macse (macse_eligible, macse_contract_id)
);

-- Real-time Telemetry Data
CREATE TABLE bess_telemetry (
    id BIGSERIAL PRIMARY KEY,
    bess_asset_id INTEGER REFERENCES bess_assets(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,

    -- State of Charge
    soc_pct DECIMAL(5,2) NOT NULL,  -- 0.00 - 100.00
    soc_kwh DECIMAL(10,3),          -- Absolute energy stored

    -- Power Flow
    power_kw DECIMAL(10,3),         -- Positive = charging, Negative = discharging
    energy_charged_kwh DECIMAL(10,3),   -- Cumulative since last reset
    energy_discharged_kwh DECIMAL(10,3), -- Cumulative since last reset

    -- Electrical Parameters
    voltage_v DECIMAL(8,2),
    current_a DECIMAL(8,2),
    frequency_hz DECIMAL(5,2),
    power_factor DECIMAL(4,3),

    -- Thermal Management
    temperature_avg_c DECIMAL(5,2),
    temperature_max_c DECIMAL(5,2),
    temperature_min_c DECIMAL(5,2),
    cooling_system_status VARCHAR(50),

    -- State of Health
    soh_pct DECIMAL(5,2),  -- 100% = new, decreases with age

    -- Operational State
    operational_mode VARCHAR(50),  -- 'idle', 'charging', 'discharging', 'standby'
    grid_connection_status VARCHAR(50),  -- 'connected', 'disconnected', 'islanded'

    -- Alarms & Warnings
    alarm_count INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    fault_codes TEXT,  -- JSON array of active fault codes

    -- Data Source
    data_source VARCHAR(50),  -- 'manual_upload', 'tesla_api', 'byd_bms', 'scada'
    data_quality VARCHAR(20),  -- 'good', 'estimated', 'questionable', 'bad'

    -- Indexes for fast queries
    INDEX idx_bess_telemetry_asset_time (bess_asset_id, timestamp DESC),
    INDEX idx_bess_telemetry_timestamp (timestamp DESC),

    -- Unique constraint (1 record per asset per timestamp)
    UNIQUE (bess_asset_id, timestamp)
);

-- Partitioning for performance (monthly partitions)
-- ALTER TABLE bess_telemetry PARTITION BY RANGE (timestamp);

-- Cycle Counting & Degradation
CREATE TABLE bess_cycles (
    id SERIAL PRIMARY KEY,
    bess_asset_id INTEGER REFERENCES bess_assets(id) ON DELETE CASCADE,

    -- Cycle Info
    cycle_start_timestamp TIMESTAMP NOT NULL,
    cycle_end_timestamp TIMESTAMP,
    cycle_type VARCHAR(20),  -- 'full', 'partial'

    -- Charge Phase
    charge_start_soc_pct DECIMAL(5,2),
    charge_end_soc_pct DECIMAL(5,2),
    charge_energy_kwh DECIMAL(10,3),
    charge_duration_minutes INTEGER,

    -- Discharge Phase
    discharge_start_soc_pct DECIMAL(5,2),
    discharge_end_soc_pct DECIMAL(5,2),
    discharge_energy_kwh DECIMAL(10,3),
    discharge_duration_minutes INTEGER,

    -- Cycle Metrics
    depth_of_discharge_pct DECIMAL(5,2),  -- Key degradation factor
    round_trip_efficiency_pct DECIMAL(5,2),
    equivalent_full_cycles DECIMAL(8,4),  -- Weighted by DoD

    -- Revenue Attribution
    purpose VARCHAR(50),  -- 'arbitrage', 'fcr', 'afrr', 'peak_shaving', 'self_consumption'
    revenue_eur DECIMAL(10,2),

    -- Indexes
    INDEX idx_bess_cycles_asset (bess_asset_id),
    INDEX idx_bess_cycles_timestamp (cycle_start_timestamp DESC)
);

-- Performance Metrics (Daily Aggregates)
CREATE TABLE bess_performance_metrics (
    id SERIAL PRIMARY KEY,
    bess_asset_id INTEGER REFERENCES bess_assets(id) ON DELETE CASCADE,
    date DATE NOT NULL,

    -- Energy Throughput
    total_energy_charged_kwh DECIMAL(10,3),
    total_energy_discharged_kwh DECIMAL(10,3),
    net_energy_kwh DECIMAL(10,3),  -- Discharged - Charged

    -- Efficiency
    round_trip_efficiency_pct DECIMAL(5,2),
    inverter_efficiency_pct DECIMAL(5,2),

    -- Cycles
    full_cycle_equivalent DECIMAL(6,3),  -- Sum of equivalent full cycles for the day
    cumulative_cycles DECIMAL(10,3),     -- Lifetime cycles

    -- Availability
    operational_hours DECIMAL(5,2),      -- Hours available for service
    unavailable_hours DECIMAL(5,2),      -- Downtime
    availability_pct DECIMAL(5,2),       -- For MACSE compliance (80% min)

    -- SOC Statistics
    avg_soc_pct DECIMAL(5,2),
    min_soc_pct DECIMAL(5,2),
    max_soc_pct DECIMAL(5,2),

    -- Degradation Tracking
    soh_start_pct DECIMAL(5,2),
    soh_end_pct DECIMAL(5,2),
    degradation_pct_per_day DECIMAL(8,6),

    -- Revenue
    total_revenue_eur DECIMAL(10,2),
    capacity_payment_eur DECIMAL(10,2),   -- MACSE
    arbitrage_revenue_eur DECIMAL(10,2),  -- Energy trading
    grid_services_revenue_eur DECIMAL(10,2),  -- FCR, aFRR

    -- Costs
    degradation_cost_eur DECIMAL(10,2),  -- Estimated cost of capacity loss

    -- Indexes
    UNIQUE (bess_asset_id, date),
    INDEX idx_bess_performance_date (date DESC)
);

-- Arbitrage Opportunities (Integration with 15-min trading)
CREATE TABLE bess_arbitrage_opportunities (
    id SERIAL PRIMARY KEY,
    bess_asset_id INTEGER REFERENCES bess_assets(id) ON DELETE CASCADE,

    -- Opportunity Window
    charge_start_timestamp TIMESTAMP NOT NULL,
    charge_price_eur_mwh DECIMAL(10,3),  -- Low price period
    discharge_start_timestamp TIMESTAMP NOT NULL,
    discharge_price_eur_mwh DECIMAL(10,3),  -- High price period

    -- Feasibility
    spread_eur_mwh DECIMAL(10,3),  -- Price difference
    net_profit_eur_mwh DECIMAL(10,3),  -- After efficiency losses
    energy_volume_kwh DECIMAL(10,2),
    estimated_profit_eur DECIMAL(10,2),

    -- Execution
    status VARCHAR(50),  -- 'identified', 'scheduled', 'executed', 'missed'
    actual_profit_eur DECIMAL(10,2),

    -- Constraints
    constraint_violated VARCHAR(200),  -- Why opportunity was missed

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),

    -- Indexes
    INDEX idx_arb_opp_asset (bess_asset_id),
    INDEX idx_arb_opp_timestamp (charge_start_timestamp),
    INDEX idx_arb_opp_status (status)
);

-- MACSE Documentation & Compliance
CREATE TABLE bess_macse_applications (
    id SERIAL PRIMARY KEY,
    bess_asset_id INTEGER REFERENCES bess_assets(id) ON DELETE CASCADE,

    -- Application Details
    auction_date DATE NOT NULL,  -- e.g., 2025-09-30
    application_submitted_date DATE,
    capacity_bid_mwh DECIMAL(10,2) NOT NULL,
    price_bid_eur_mwh_year DECIMAL(10,2),

    -- Technical Documentation
    technical_spec_document_url VARCHAR(500),
    terna_connection_approval_url VARCHAR(500),
    insurance_certificate_url VARCHAR(500),

    -- Award Results
    award_status VARCHAR(50),  -- 'pending', 'awarded', 'rejected'
    capacity_awarded_mwh DECIMAL(10,2),
    final_price_eur_mwh_year DECIMAL(10,2),
    contract_start_date DATE,
    contract_end_date DATE,

    -- Compliance Tracking
    monthly_availability_pct DECIMAL(5,2),  -- Must maintain 80%+
    penalty_incurred_eur DECIMAL(10,2),

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_macse_asset (bess_asset_id),
    INDEX idx_macse_auction (auction_date)
);
```

### 3.2 Core Services

**File: `app/services/bess/bess_telemetry_service.py`**

```python
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
import pandas as pd
import numpy as np

from app.models.bess import BESSAsset, BESSTelemetry, BESSCycle, BESSPerformanceMetrics
from app.schemas.bess import (
    BESSTelemetryCreate, BESSTelemetryResponse,
    BESSPerformanceResponse, CycleAnalysisResponse
)
from app.services.base_service import BaseService

class BESSTelemetryService(BaseService[BESSTelemetry]):
    """Service for BESS telemetry data management and analysis"""

    def __init__(self, session: AsyncSession):
        super().__init__(BESSTelemetry, session)
        self.session = session

    async def ingest_telemetry_batch(
        self,
        bess_asset_id: int,
        telemetry_data: List[BESSTelemetryCreate],
        data_source: str = "manual_upload"
    ) -> Dict[str, Any]:
        """
        Ingest batch of telemetry records (from CSV upload or API)

        Returns:
            {
                "records_inserted": int,
                "records_updated": int,
                "records_skipped": int,
                "cycles_detected": int
            }
        """
        records_inserted = 0
        records_updated = 0
        records_skipped = 0

        for record in telemetry_data:
            # Check if record exists (upsert pattern)
            existing = await self.session.execute(
                select(BESSTelemetry).where(
                    and_(
                        BESSTelemetry.bess_asset_id == bess_asset_id,
                        BESSTelemetry.timestamp == record.timestamp
                    )
                )
            )
            existing_record = existing.scalar_one_or_none()

            if existing_record:
                # Update existing record
                for key, value in record.dict(exclude_unset=True).items():
                    setattr(existing_record, key, value)
                existing_record.data_source = data_source
                records_updated += 1
            else:
                # Insert new record
                new_telemetry = BESSTelemetry(
                    bess_asset_id=bess_asset_id,
                    data_source=data_source,
                    **record.dict()
                )
                self.session.add(new_telemetry)
                records_inserted += 1

        await self.session.commit()

        # Detect and count cycles
        cycles_detected = await self._detect_cycles(bess_asset_id)

        return {
            "records_inserted": records_inserted,
            "records_updated": records_updated,
            "records_skipped": records_skipped,
            "cycles_detected": cycles_detected
        }

    async def get_current_state(self, bess_asset_id: int) -> Optional[BESSTelemetryResponse]:
        """Get most recent telemetry record for BESS asset"""
        result = await self.session.execute(
            select(BESSTelemetry)
            .where(BESSTelemetry.bess_asset_id == bess_asset_id)
            .order_by(desc(BESSTelemetry.timestamp))
            .limit(1)
        )
        latest = result.scalar_one_or_none()

        if latest:
            return BESSTelemetryResponse.from_orm(latest)
        return None

    async def get_telemetry_timeseries(
        self,
        bess_asset_id: int,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "1min"
    ) -> List[BESSTelemetryResponse]:
        """
        Get telemetry time series for charting

        Args:
            granularity: '1min', '5min', '15min', '1hour'
        """
        result = await self.session.execute(
            select(BESSTelemetry)
            .where(
                and_(
                    BESSTelemetry.bess_asset_id == bess_asset_id,
                    BESSTelemetry.timestamp >= start_date,
                    BESSTelemetry.timestamp <= end_date
                )
            )
            .order_by(BESSTelemetry.timestamp)
        )
        records = result.scalars().all()

        # TODO: Implement downsampling for granularity > 1min

        return [BESSTelemetryResponse.from_orm(r) for r in records]

    async def calculate_performance_metrics(
        self,
        bess_asset_id: int,
        date: datetime.date
    ) -> BESSPerformanceResponse:
        """
        Calculate daily performance metrics

        Metrics:
        - Energy charged/discharged
        - Round-trip efficiency
        - Cycle count
        - Availability %
        - SOC statistics
        """
        start_datetime = datetime.combine(date, datetime.min.time())
        end_datetime = start_datetime + timedelta(days=1)

        # Get all telemetry for the day
        result = await self.session.execute(
            select(BESSTelemetry)
            .where(
                and_(
                    BESSTelemetry.bess_asset_id == bess_asset_id,
                    BESSTelemetry.timestamp >= start_datetime,
                    BESSTelemetry.timestamp < end_datetime
                )
            )
            .order_by(BESSTelemetry.timestamp)
        )
        telemetry_records = result.scalars().all()

        if not telemetry_records:
            return None

        # Convert to pandas for easier analysis
        df = pd.DataFrame([
            {
                'timestamp': r.timestamp,
                'soc_pct': r.soc_pct,
                'power_kw': r.power_kw,
                'energy_charged_kwh': r.energy_charged_kwh,
                'energy_discharged_kwh': r.energy_discharged_kwh,
                'soh_pct': r.soh_pct,
                'operational_mode': r.operational_mode
            }
            for r in telemetry_records
        ])

        # Calculate metrics
        total_charged = df['energy_charged_kwh'].max() - df['energy_charged_kwh'].min()
        total_discharged = df['energy_discharged_kwh'].max() - df['energy_discharged_kwh'].min()

        # Round-trip efficiency
        rte_pct = (total_discharged / total_charged * 100) if total_charged > 0 else 0

        # Availability (non-fault time / total time)
        operational_minutes = len(df[df['operational_mode'].isin(['idle', 'charging', 'discharging', 'standby'])])
        total_minutes = len(df)
        availability_pct = (operational_minutes / total_minutes * 100) if total_minutes > 0 else 0

        # SOC statistics
        avg_soc = df['soc_pct'].mean()
        min_soc = df['soc_pct'].min()
        max_soc = df['soc_pct'].max()

        # SOH degradation
        soh_start = df.iloc[0]['soh_pct']
        soh_end = df.iloc[-1]['soh_pct']
        degradation_per_day = soh_start - soh_end if pd.notna(soh_start) and pd.notna(soh_end) else 0

        # Get cycle count for the day
        cycles_result = await self.session.execute(
            select(func.sum(BESSCycle.equivalent_full_cycles))
            .where(
                and_(
                    BESSCycle.bess_asset_id == bess_asset_id,
                    BESSCycle.cycle_start_timestamp >= start_datetime,
                    BESSCycle.cycle_start_timestamp < end_datetime
                )
            )
        )
        full_cycle_equivalent = cycles_result.scalar() or 0

        # Create or update performance record
        performance = BESSPerformanceMetrics(
            bess_asset_id=bess_asset_id,
            date=date,
            total_energy_charged_kwh=total_charged,
            total_energy_discharged_kwh=total_discharged,
            net_energy_kwh=total_discharged - total_charged,
            round_trip_efficiency_pct=rte_pct,
            full_cycle_equivalent=full_cycle_equivalent,
            operational_hours=operational_minutes / 60,
            unavailable_hours=(total_minutes - operational_minutes) / 60,
            availability_pct=availability_pct,
            avg_soc_pct=avg_soc,
            min_soc_pct=min_soc,
            max_soc_pct=max_soc,
            soh_start_pct=soh_start,
            soh_end_pct=soh_end,
            degradation_pct_per_day=degradation_per_day
        )

        # Upsert
        existing = await self.session.execute(
            select(BESSPerformanceMetrics).where(
                and_(
                    BESSPerformanceMetrics.bess_asset_id == bess_asset_id,
                    BESSPerformanceMetrics.date == date
                )
            )
        )
        existing_record = existing.scalar_one_or_none()

        if existing_record:
            for key, value in performance.__dict__.items():
                if not key.startswith('_'):
                    setattr(existing_record, key, value)
        else:
            self.session.add(performance)

        await self.session.commit()

        return BESSPerformanceResponse.from_orm(performance if not existing_record else existing_record)

    async def _detect_cycles(self, bess_asset_id: int) -> int:
        """
        Detect charge/discharge cycles from telemetry data

        A cycle is defined as:
        1. Charge phase: SOC increases by >10%
        2. Discharge phase: SOC decreases by >10%

        Returns number of new cycles detected.
        """
        # Get latest telemetry (last 7 days to catch partial cycles)
        start_date = datetime.now() - timedelta(days=7)

        result = await self.session.execute(
            select(BESSTelemetry)
            .where(
                and_(
                    BESSTelemetry.bess_asset_id == bess_asset_id,
                    BESSTelemetry.timestamp >= start_date
                )
            )
            .order_by(BESSTelemetry.timestamp)
        )
        records = result.scalars().all()

        if len(records) < 2:
            return 0

        cycles_detected = 0
        current_cycle = None

        for i in range(1, len(records)):
            prev = records[i-1]
            curr = records[i]

            soc_change = curr.soc_pct - prev.soc_pct

            # Detect charging phase start
            if soc_change > 0 and current_cycle is None:
                current_cycle = {
                    'charge_start': prev,
                    'charge_end': None,
                    'discharge_start': None,
                    'discharge_end': None
                }

            # Detect charging phase end (SOC plateaus or starts decreasing)
            elif soc_change <= 0 and current_cycle and current_cycle['charge_end'] is None:
                current_cycle['charge_end'] = prev

            # Detect discharging phase start
            elif soc_change < 0 and current_cycle and current_cycle['charge_end']:
                current_cycle['discharge_start'] = prev

            # Detect discharging phase end (SOC plateaus or starts increasing)
            elif soc_change >= 0 and current_cycle and current_cycle['discharge_start']:
                current_cycle['discharge_end'] = prev

                # Complete cycle detected - calculate metrics and save
                depth_of_discharge = current_cycle['charge_end'].soc_pct - current_cycle['discharge_end'].soc_pct

                if depth_of_discharge >= 10:  # Minimum 10% DoD to count as cycle
                    charge_energy = current_cycle['charge_end'].energy_charged_kwh - current_cycle['charge_start'].energy_charged_kwh
                    discharge_energy = current_cycle['discharge_end'].energy_discharged_kwh - current_cycle['discharge_start'].energy_discharged_kwh

                    rte = (discharge_energy / charge_energy * 100) if charge_energy > 0 else 0

                    # Equivalent full cycle (weighted by DoD)
                    # 100% DoD = 1.0 EFC, 50% DoD = 0.5 EFC
                    efc = depth_of_discharge / 100.0

                    cycle_record = BESSCycle(
                        bess_asset_id=bess_asset_id,
                        cycle_start_timestamp=current_cycle['charge_start'].timestamp,
                        cycle_end_timestamp=current_cycle['discharge_end'].timestamp,
                        cycle_type='full' if depth_of_discharge >= 80 else 'partial',
                        charge_start_soc_pct=current_cycle['charge_start'].soc_pct,
                        charge_end_soc_pct=current_cycle['charge_end'].soc_pct,
                        charge_energy_kwh=charge_energy,
                        discharge_start_soc_pct=current_cycle['discharge_start'].soc_pct,
                        discharge_end_soc_pct=current_cycle['discharge_end'].soc_pct,
                        discharge_energy_kwh=discharge_energy,
                        depth_of_discharge_pct=depth_of_discharge,
                        round_trip_efficiency_pct=rte,
                        equivalent_full_cycles=efc
                    )

                    self.session.add(cycle_record)
                    cycles_detected += 1

                # Reset for next cycle
                current_cycle = None

        if cycles_detected > 0:
            await self.session.commit()

        return cycles_detected
```

**File: `app/services/bess/arbitrage_optimizer_service.py`**

```python
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.bess import BESSAsset, BESSArbitrageOpportunity
from app.models.market import MarketPrices15Min  # From 15-min trading module
from app.schemas.bess import ArbitrageOpportunityCreate, ArbitrageOpportunityResponse

class ArbitrageOptimizerService:
    """
    Identifies profitable arbitrage opportunities by analyzing
    15-minute price forecasts and BESS availability
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def identify_opportunities(
        self,
        bess_asset_id: int,
        forecast_hours: int = 24
    ) -> List[ArbitrageOpportunityResponse]:
        """
        Scan next 24 hours for profitable charge/discharge windows

        Algorithm:
        1. Get 15-min price forecast for next 24 hours
        2. Find lowest-price charging windows
        3. Find highest-price discharging windows
        4. Calculate net profit after efficiency losses
        5. Check BESS constraints (SOC, power limits)
        """
        # Get BESS asset details
        bess_result = await self.session.execute(
            select(BESSAsset).where(BESSAsset.id == bess_asset_id)
        )
        bess = bess_result.scalar_one()

        # Get 15-minute price forecast
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=forecast_hours)

        prices_result = await self.session.execute(
            select(MarketPrices15Min)
            .where(
                and_(
                    MarketPrices15Min.timestamp >= start_time,
                    MarketPrices15Min.timestamp <= end_time,
                    MarketPrices15Min.zone == bess.site.zone  # Assume site has zone field
                )
            )
            .order_by(MarketPrices15Min.timestamp)
        )
        price_forecast = prices_result.scalars().all()

        if len(price_forecast) < 8:  # Need at least 2 hours of data
            return []

        opportunities = []

        # Sort prices to find best charge/discharge windows
        sorted_prices = sorted(price_forecast, key=lambda p: p.price_eur_mwh)

        # Find low-price charging windows (bottom 25%)
        charge_windows = sorted_prices[:len(sorted_prices)//4]

        # Find high-price discharging windows (top 25%)
        discharge_windows = sorted(sorted_prices[-len(sorted_prices)//4:],
                                   key=lambda p: p.price_eur_mwh,
                                   reverse=True)

        # Pair charge and discharge windows
        for charge_window in charge_windows:
            for discharge_window in discharge_windows:
                # Discharge must be after charge
                if discharge_window.timestamp <= charge_window.timestamp:
                    continue

                # Calculate spread
                spread = discharge_window.price_eur_mwh - charge_window.price_eur_mwh

                # Must be positive spread
                if spread <= 0:
                    continue

                # Account for round-trip efficiency
                efficiency_loss = 1 - (bess.round_trip_efficiency_pct / 100)
                net_profit_per_mwh = spread * (1 - efficiency_loss)

                # Minimum profitability threshold (€5/MWh)
                if net_profit_per_mwh < 5:
                    continue

                # Calculate energy volume (assume full charge/discharge)
                energy_kwh = bess.usable_capacity_kwh
                estimated_profit = (energy_kwh / 1000) * net_profit_per_mwh

                # Create opportunity record
                opportunity = BESSArbitrageOpportunity(
                    bess_asset_id=bess_asset_id,
                    charge_start_timestamp=charge_window.timestamp,
                    charge_price_eur_mwh=charge_window.price_eur_mwh,
                    discharge_start_timestamp=discharge_window.timestamp,
                    discharge_price_eur_mwh=discharge_window.price_eur_mwh,
                    spread_eur_mwh=spread,
                    net_profit_eur_mwh=net_profit_per_mwh,
                    energy_volume_kwh=energy_kwh,
                    estimated_profit_eur=estimated_profit,
                    status='identified'
                )

                self.session.add(opportunity)
                opportunities.append(ArbitrageOpportunityResponse.from_orm(opportunity))

        await self.session.commit()

        # Sort by profit and return top opportunities
        opportunities.sort(key=lambda o: o.estimated_profit_eur, reverse=True)
        return opportunities[:10]  # Top 10 opportunities
```

### 3.3 API Endpoints

**File: `app/api/v1/bess.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, date
import pandas as pd

from app.database import get_session
from app.schemas.bess import *
from app.services.bess.bess_asset_service import BESSAssetService
from app.services.bess.bess_telemetry_service import BESSTelemetryService
from app.services.bess.arbitrage_optimizer_service import ArbitrageOptimizerService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/bess", tags=["BESS"])

# ==================== BESS Assets ====================

@router.post("/assets", response_model=BESSAssetResponse)
async def create_bess_asset(
    asset_data: BESSAssetCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Create new BESS asset

    Example:
    ```json
    {
      "name": "Megapack Site A",
      "site_id": 10,
      "manufacturer": "Tesla",
      "model": "Megapack 2XL",
      "nominal_capacity_kwh": 3916,
      "usable_capacity_kwh": 3524,
      "nominal_power_kw": 1927,
      "chemistry": "LFP",
      "round_trip_efficiency_pct": 89.5,
      "macse_eligible": true,
      "data_source": "api",
      "vendor_api_endpoint": "https://api.tesla.com/energy"
    }
    ```
    """
    service = BESSAssetService(session)
    asset = await service.create_bess_asset(
        tenant_id=current_user.tenant_id,
        asset_data=asset_data
    )
    return asset

@router.get("/assets/{asset_id}", response_model=BESSAssetDetailResponse)
async def get_bess_asset(
    asset_id: int,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """Get BESS asset details with current state"""
    asset_service = BESSAssetService(session)
    telemetry_service = BESSTelemetryService(session)

    asset = await asset_service.get_by_id(asset_id)
    if not asset or asset.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="BESS asset not found")

    # Get current telemetry
    current_state = await telemetry_service.get_current_state(asset_id)

    # Get today's performance
    today_performance = await telemetry_service.calculate_performance_metrics(
        asset_id,
        date.today()
    )

    return {
        **asset.dict(),
        "current_state": current_state,
        "today_performance": today_performance
    }

@router.get("/assets", response_model=List[BESSAssetResponse])
async def list_bess_assets(
    site_id: Optional[int] = None,
    macse_eligible: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """List all BESS assets for tenant"""
    service = BESSAssetService(session)
    assets = await service.list_assets(
        tenant_id=current_user.tenant_id,
        site_id=site_id,
        macse_eligible=macse_eligible
    )
    return assets

# ==================== Telemetry ====================

@router.post("/assets/{asset_id}/telemetry/upload")
async def upload_telemetry_csv(
    asset_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Upload telemetry CSV file

    CSV Format:
    ```
    timestamp,soc_pct,power_kw,voltage_v,current_a,temperature_avg_c,soh_pct
    2025-01-15 10:00:00,45.2,1500.0,800.5,1875.0,25.3,98.5
    2025-01-15 10:01:00,45.8,1480.0,801.2,1850.2,25.4,98.5
    ...
    ```
    """
    # Verify asset ownership
    asset_service = BESSAssetService(session)
    asset = await asset_service.get_by_id(asset_id)
    if not asset or asset.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="BESS asset not found")

    # Read CSV
    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")

    # Validate required columns
    required_cols = ['timestamp', 'soc_pct', 'power_kw']
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {missing_cols}"
        )

    # Convert to telemetry records
    telemetry_records = []
    for _, row in df.iterrows():
        telemetry_records.append(
            BESSTelemetryCreate(
                timestamp=pd.to_datetime(row['timestamp']),
                soc_pct=row['soc_pct'],
                power_kw=row['power_kw'],
                voltage_v=row.get('voltage_v'),
                current_a=row.get('current_a'),
                temperature_avg_c=row.get('temperature_avg_c'),
                soh_pct=row.get('soh_pct'),
                operational_mode='charging' if row['power_kw'] > 0 else 'discharging' if row['power_kw'] < 0 else 'idle'
            )
        )

    # Ingest batch
    service = BESSTelemetryService(session)
    result = await service.ingest_telemetry_batch(
        bess_asset_id=asset_id,
        telemetry_data=telemetry_records,
        data_source="manual_upload"
    )

    return {
        "message": "Telemetry uploaded successfully",
        **result
    }

@router.get("/assets/{asset_id}/telemetry/current", response_model=BESSTelemetryResponse)
async def get_current_telemetry(
    asset_id: int,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """Get most recent telemetry for BESS"""
    service = BESSTelemetryService(session)
    telemetry = await service.get_current_state(asset_id)

    if not telemetry:
        raise HTTPException(status_code=404, detail="No telemetry data available")

    return telemetry

@router.get("/assets/{asset_id}/telemetry/timeseries", response_model=List[BESSTelemetryResponse])
async def get_telemetry_timeseries(
    asset_id: int,
    start_date: datetime,
    end_date: datetime,
    granularity: str = "1min",
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Get telemetry time series for charting

    Query params:
    - start_date: ISO datetime (e.g., 2025-01-15T00:00:00)
    - end_date: ISO datetime
    - granularity: '1min', '5min', '15min', '1hour'
    """
    service = BESSTelemetryService(session)
    data = await service.get_telemetry_timeseries(
        bess_asset_id=asset_id,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity
    )
    return data

# ==================== Performance Metrics ====================

@router.get("/assets/{asset_id}/performance/daily", response_model=BESSPerformanceResponse)
async def get_daily_performance(
    asset_id: int,
    date: date,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """Get performance metrics for specific date"""
    service = BESSTelemetryService(session)
    performance = await service.calculate_performance_metrics(asset_id, date)

    if not performance:
        raise HTTPException(status_code=404, detail="No data available for this date")

    return performance

@router.get("/assets/{asset_id}/cycles", response_model=List[CycleAnalysisResponse])
async def get_cycle_history(
    asset_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """Get cycle history with degradation analysis"""
    # TODO: Implement cycle history retrieval
    pass

# ==================== Arbitrage Opportunities ====================

@router.post("/assets/{asset_id}/arbitrage/scan", response_model=List[ArbitrageOpportunityResponse])
async def scan_arbitrage_opportunities(
    asset_id: int,
    forecast_hours: int = 24,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Scan for profitable arbitrage opportunities

    Analyzes 15-minute price forecast and identifies:
    - Low-price charging windows
    - High-price discharging windows
    - Net profit after efficiency losses

    Returns top 10 opportunities sorted by profit
    """
    service = ArbitrageOptimizerService(session)
    opportunities = await service.identify_opportunities(
        bess_asset_id=asset_id,
        forecast_hours=forecast_hours
    )
    return opportunities

@router.get("/assets/{asset_id}/arbitrage/opportunities", response_model=List[ArbitrageOpportunityResponse])
async def list_arbitrage_opportunities(
    asset_id: int,
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """List all identified arbitrage opportunities"""
    # TODO: Implement opportunity listing
    pass

# ==================== MACSE Applications ====================

@router.post("/assets/{asset_id}/macse/application", response_model=MACSEApplicationResponse)
async def create_macse_application(
    asset_id: int,
    application_data: MACSEApplicationCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Create MACSE auction application

    Documents required:
    - Technical specifications (Terna A.79 compliance)
    - Grid connection approval
    - Insurance certificate
    - Performance history (6+ months preferred)
    """
    # TODO: Implement MACSE application creation
    pass

@router.get("/assets/{asset_id}/macse/compliance", response_model=MACSEComplianceReport)
async def get_macse_compliance_report(
    asset_id: int,
    month: int,
    year: int,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Generate monthly MACSE compliance report

    Includes:
    - Availability % (must be ≥80%)
    - Response time metrics
    - Energy delivered
    - Penalties incurred (if any)
    """
    # TODO: Implement compliance reporting
    pass
```

---

## 4. Implementation Plan

### Phase 1A: Foundation (Weeks 1-4)

**Week 1: Database & Models**
- [ ] Create database schema (5 tables)
- [ ] SQLAlchemy models for BESS entities
- [ ] Pydantic schemas for API
- [ ] Database migrations
- [ ] Unit tests for models

**Week 2: Manual Telemetry Import**
- [ ] CSV upload endpoint
- [ ] Pandas-based CSV parsing
- [ ] Validation & error handling
- [ ] Bulk insert optimization
- [ ] Test with sample Tesla/BYD data

**Week 3: Performance Calculation Engine**
- [ ] Daily metrics calculation service
- [ ] Cycle detection algorithm
- [ ] Round-trip efficiency calculation
- [ ] SOH degradation tracking
- [ ] Automated nightly jobs (Celery)

**Week 4: Basic Dashboard**
- [ ] Current state widget (SOC, power, temp)
- [ ] Performance charts (Recharts.js)
- [ ] Cycle history table
- [ ] Alerts for low SOH
- [ ] Export reports (PDF)

**Deliverable:** Operators can upload telemetry CSVs and view performance metrics

---

### Phase 1B: Vendor Integration (Weeks 5-8)

**Week 5: Tesla Megapack API**
- [ ] OAuth authentication
- [ ] Real-time telemetry polling
- [ ] API error handling & retry logic
- [ ] Rate limiting compliance
- [ ] Test with Tesla demo account

**Week 6: BYD & Huawei APIs**
- [ ] BYD Battery Management System API
- [ ] Huawei FusionSolar integration
- [ ] Multi-vendor data normalization
- [ ] Vendor-agnostic data model
- [ ] Integration tests

**Week 7: Arbitrage Opportunity Scanner**
- [ ] Integration with 15-min trading module
- [ ] Price spread calculator
- [ ] Efficiency-adjusted profit estimation
- [ ] Opportunity ranking algorithm
- [ ] Email/SMS alerts for top opportunities

**Week 8: MACSE Documentation Builder**
- [ ] Technical spec generator
- [ ] Performance history export
- [ ] Terna A.79 compliance checklist
- [ ] Application PDF builder
- [ ] Mock application submission

**Deliverable:** Automated telemetry collection + arbitrage alerts

---

### Phase 1C: MACSE Preparation (Weeks 9-10)

**Week 9: MACSE Application Module**
- [ ] Application form UI
- [ ] Document upload (S3/MinIO)
- [ ] Compliance checklist
- [ ] Bid calculator (€37k starting price)
- [ ] Application status tracking

**Week 10: Testing & Documentation**
- [ ] End-to-end testing with 3 BESS types
- [ ] Load testing (10,000 telemetry records/min)
- [ ] User documentation
- [ ] API documentation (Swagger)
- [ ] Deployment to staging

**Deliverable:** Production-ready BESS monitoring + MACSE application tool

---

## 5. Revenue Model & Pricing

### 5.1 Pricing Tiers

**Tier 1: Basic Monitoring**
- **Price:** €200/MWh/month
- **Features:**
  - Manual telemetry upload (CSV)
  - Daily performance reports
  - Cycle counting & degradation tracking
  - Basic dashboard
  - Email alerts
- **Target:** Small C&I installations (0.5-2 MWh)

**Tier 2: Automated Monitoring + Optimization**
- **Price:** €500/MWh/month
- **Features:**
  - All Basic features
  - Vendor API integration (Tesla, BYD, Huawei)
  - Real-time telemetry (1-min)
  - Arbitrage opportunity alerts
  - 15-minute trading integration
  - Advanced analytics
- **Target:** Mid-size projects (2-10 MWh)

**Tier 3: Enterprise + MACSE**
- **Price:** €1,000/MWh/month
- **Features:**
  - All Automated features
  - MACSE application builder
  - Compliance reporting
  - SCADA integration (Phase 2)
  - Dedicated support
  - Custom integrations
- **Target:** Utility-scale (10+ MWh), MACSE participants

**One-Time Services:**
- MACSE application preparation: €10,000-€15,000
- SCADA integration: €20,000-€50,000
- Custom vendor integration: €15,000-€30,000

### 5.2 Revenue Projections

**Year 1 (2025):**
- 10 customers @ Tier 2 (avg 5 MWh each): 50 MWh
- MRR: 50 MWh × €500 = €25,000
- ARR: €300,000
- MACSE applications (5 customers): €50,000
- **Total Y1 Revenue:** €350,000

**Year 2 (2026):**
- 50 customers (30 Tier 2, 20 Tier 3): 500 MWh
- MRR: €350,000
- ARR: €4.2M
- MACSE applications: €150,000
- **Total Y2 Revenue:** €4.35M

**Year 3 (2027):**
- 150 customers: 2,000 MWh
- ARR: €15M
- Services: €500,000
- **Total Y3 Revenue:** €15.5M

---

## 6. Competitive Differentiation

### What Makes SentricS2 BESS Module Unique?

**1. MACSE-First Design**
- Only platform with built-in MACSE application builder
- Automated compliance tracking (80% availability monitoring)
- Terna A.79 checklist & documentation generator
- **Competitor Gap:** No existing platforms target Italian MACSE market

**2. Integration with 15-Minute Trading**
- Real-time arbitrage opportunity detection
- Automated charge/discharge scheduling based on price forecasts
- Negative price protection (curtailment alerts)
- **Competitor Gap:** Most BESS platforms don't integrate with TIDE market

**3. Multi-Vendor Support from Day 1**
- Tesla, BYD, Huawei, Sungrow, Fluence
- Vendor-agnostic data model
- Standardized APIs regardless of hardware
- **Competitor Gap:** Most platforms lock into single vendor ecosystem

**4. Advanced Degradation Analytics**
- Cycle-by-cycle SOH tracking
- Depth-of-discharge weighting (EFC calculation)
- End-of-life forecasting
- Warranty compliance monitoring
- **Competitor Gap:** Most platforms only show basic SOC, not degradation trends

**5. Italian Market Specialization**
- Zone-specific pricing integration (7 Italian zones)
- Terna TSO compliance
- Italian language UI
- Local support & consulting
- **Competitor Gap:** Global platforms don't understand Italian regulatory nuances

---

## 7. Technical Risks & Mitigation

### Risk 1: Vendor API Limitations
**Risk:** Tesla/BYD APIs may have rate limits or incomplete data
**Mitigation:**
- Implement intelligent polling (adaptive intervals)
- Fallback to manual CSV import
- Cache historical data locally
- Negotiate API access with vendors

### Risk 2: MACSE Auction Timing
**Risk:** September 30, 2025 deadline is tight
**Mitigation:**
- Prioritize MACSE features in sprint planning
- Early access program with 5 beta customers
- Parallel development of documentation builder
- Contingency: Offer MACSE services manually if software not ready

### Risk 3: SCADA Integration Complexity
**Risk:** IEC 61850 integration requires specialized knowledge
**Mitigation:**
- Partner with SCADA integration firms (e.g., Schneider Electric)
- Offer SCADA as premium add-on service
- Hire experienced SCADA engineer in Phase 2
- Start with Modbus TCP (simpler protocol) in Phase 1

### Risk 4: Data Volume & Storage Costs
**Risk:** 1-minute telemetry = 1,440 records/day/asset × 100 assets = 144k records/day
**Mitigation:**
- Implement database partitioning (monthly)
- Downsample historical data (keep 1-min for 30 days, then aggregate to 15-min)
- Use TimescaleDB extension for PostgreSQL
- Compress old data with pg_compression

### Risk 5: Competition from Utility-Scale Players
**Risk:** Fluence, Tesla, Wärtsilä have their own monitoring platforms
**Mitigation:**
- Target multi-vendor operators (not single-vendor fleets)
- Focus on smaller operators (1-50 MWh) underserved by large vendors
- Differentiate with Italian market expertise
- Bundle with CER billing & 15-min trading (unique combo)

---

## 8. Success Metrics

### Technical Metrics (Phase 1)
- [ ] Support 5 BESS vendors (Tesla, BYD, Huawei, Sungrow, Fluence)
- [ ] Ingest 10,000 telemetry records/minute
- [ ] Calculate performance metrics within 5 minutes of daily rollover
- [ ] Detect cycles with 95%+ accuracy
- [ ] Dashboard load time <2 seconds

### Business Metrics (Q2-Q3 2025)
- [ ] Sign 10 paying customers by end of Q2
- [ ] 50 MWh under monitoring by end of Q3
- [ ] 5 MACSE applications submitted (September 30, 2025)
- [ ] 2+ customers win MACSE capacity awards
- [ ] €300k ARR by end of 2025

### Customer Satisfaction
- [ ] NPS score 50+
- [ ] 90%+ uptime SLA
- [ ] <5 minute response time for critical alerts
- [ ] 100% of MACSE applications meet Terna documentation requirements

---

## 9. Next Steps

### Immediate Actions (Week 1)
1. **Validate with Early Customers**
   - Interview 5 BESS operators about monitoring pain points
   - Get sample telemetry data (CSV) from Tesla, BYD, Huawei systems
   - Confirm MACSE participation interest

2. **Finalize Technical Architecture**
   - Review database schema with senior engineer
   - Confirm vendor API access (register for Tesla/BYD developer accounts)
   - Set up TimescaleDB extension for time-series optimization

3. **Start Development**
   - Create database migrations
   - Build basic CRUD for bess_assets table
   - Implement CSV upload endpoint
   - Create simple dashboard mockup

4. **Regulatory Research**
   - Download Terna A.79 document (Italian)
   - Review MACSE auction rules in detail
   - Consult with Italian energy lawyer on data compliance

### Questions to Resolve
- **SCADA Integration:** Should we build in-house or partner with SCADA integration firm?
- **Vendor Priorities:** Which vendor API to integrate first (Tesla most popular, but is BYD easier)?
- **MACSE Services:** Offer full-service MACSE application prep, or software-only?
- **Pricing Strategy:** Should we charge per MWh or per asset (flat rate)?

---

## 10. Conclusion

The **BESS Basic Monitoring Module** positions SentricS2 as the leading platform for Italian battery storage operators participating in the MACSE auction and capitalizing on TIDE 15-minute arbitrage opportunities.

**Key Value Propositions:**
1. **MACSE Readiness:** Only platform with built-in application builder
2. **Arbitrage Optimization:** Integration with 15-minute trading module
3. **Multi-Vendor:** Support all major manufacturers
4. **Italian Expertise:** Zone-specific pricing, Terna compliance

**Market Timing:**
- MACSE auction: September 30, 2025 (6 months to prepare customers)
- TIDE implementation: Already active (immediate arbitrage opportunities)
- EU funding: €17.7B allocated 2024-2030 (demand surge expected)

**Revenue Potential:**
- €350k ARR in Year 1
- €4.35M ARR in Year 2
- €15.5M ARR in Year 3
- Path to €50M+ by 2028 as market matures

**This specification provides a complete blueprint for 10-week implementation delivering immediate value to Italy's fastest-growing energy market segment.**
