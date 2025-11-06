# Phase 1 - CER Billing Module - Technical Specification

**Version:** 1.0
**Date:** January 2025
**Status:** Ready for Implementation
**Priority:** HIGHEST (Solves #1 pain point)

---

## Executive Summary

The CER Billing Module automates the complex process of calculating, distributing, and managing incentives for Renewable Energy Communities (CER) in Italy. Based on extensive market research, this addresses the **#1 pain point**: 6+ month GSE delays, complex manual calculations, and member distrust.

**Market Opportunity:**
- 212 operational CERs + 600 in formation
- 80% of members expect €100/year but receive €50 (expectation gap)
- Manual processes causing delays and errors
- Revenue potential: €960K-3.8M annually

---

## Table of Contents

1. [Business Requirements](#business-requirements)
2. [Technical Architecture](#technical-architecture)
3. [GSE Integration](#gse-integration)
4. [Calculation Engine](#calculation-engine)
5. [Member Portal](#member-portal)
6. [Database Schema](#database-schema)
7. [API Endpoints](#api-endpoints)
8. [Implementation Plan](#implementation-plan)

---

## Business Requirements

### Core Functionality

1. **Automated Incentive Calculation**
   - Calculate shared energy hourly (MIN of production vs consumption)
   - Apply GSE incentive formulas automatically
   - Support multiple distribution models
   - Handle regional bonuses

2. **GSE Portal Integration**
   - Submit data to GSE portals
   - Track application status
   - Monitor response times
   - Handle compliance verification

3. **Member Portal**
   - Real-time earnings dashboard
   - Transparent calculation breakdown
   - Historical performance
   - Downloadable statements

4. **Payment Automation**
   - Generate invoices
   - Track payments
   - Handle tax documentation
   - Banking integration

### Key Pain Points Addressed

| Problem | Solution | Impact |
|---------|----------|--------|
| 6-month GSE delays | Automated submission & tracking | 80% time reduction |
| Complex calculations | Pre-programmed formulas | 100% accuracy |
| Member distrust | Transparent portal | Trust building |
| Expectation gap (€100 vs €50) | Realistic forecasting | Satisfaction improvement |
| Manual billing | Full automation | 90% cost reduction |

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     CER Billing Module                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ GSE Portal   │───▶│ Calculation  │───▶│   Member     │  │
│  │ Integration  │    │    Engine    │    │   Portal     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Data Import  │    │ Distribution │    │  Reporting   │  │
│  │   Service    │    │   Formulas   │    │   Engine     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         └────────────────────┴────────────────────┘          │
│                              │                               │
│                    ┌─────────▼─────────┐                     │
│                    │   Database        │                     │
│                    │   - Measurements  │                     │
│                    │   - Calculations  │                     │
│                    │   - Payments      │                     │
│                    └───────────────────┘                     │
└─────────────────────────────────────────────────────────────┘

External Integrations:
├── GSE Portals (Area Clienti, SPC)
├── E-Distribuzione (Metering data)
├── Terna (Grid data)
└── Banking APIs (Payments)
```

---

## GSE Integration

### Research Findings

Based on web research, GSE provides:
- **Portal:** https://areaclienti.gse.it/
- **Application:** SPC (Sistemi di Produzione e Consumo)
- **Authentication:** SPID or User ID/Password
- **Manual:** "Guida all'utilizzo dell'applicazione SPC"
- **API Status:** NO public APIs found - web portal only

### Integration Approach

**Phase 1A (Immediate):**
- Manual data export from GSE portal
- CSV/Excel import into SentricS2
- Automated calculation on imported data
- Status tracking via manual updates

**Phase 1B (3-6 months):**
- GSE portal web scraping (if legally permitted)
- Automated login via Selenium/Playwright
- Data extraction from portal pages
- Automatic status monitoring

**Phase 2 (Future):**
- Official API integration (when/if available)
- Request API access from GSE
- Real-time data synchronization

### Data Flow

```python
# GSE Data Import Flow
1. CER Administrator exports data from GSE portal
   - Energy production measurements (hourly)
   - Energy consumption measurements (hourly)
   - Incentive calculations (if available)
   - Application status

2. Upload to SentricS2
   - CSV/Excel file upload
   - Data validation
   - Automatic parsing

3. SentricS2 Processing
   - Store measurements
   - Calculate shared energy
   - Apply incentive formulas
   - Generate member allocations

4. Member Notifications
   - Email with earnings update
   - SMS alerts (optional)
   - Portal notifications
```

### GSE Portal Screens to Integrate

1. **Area Clienti Dashboard**
   - Application status
   - Document upload status
   - Communication history

2. **SPC Application**
   - Energy measurements upload
   - Configuration management
   - Member registration

3. **Incentive Management**
   - TCEC tariff rates
   - Regional bonuses
   - Payment tracking

---

## Calculation Engine

### GSE Incentive Formulas

Based on research, the calculation follows these steps:

#### 1. Shared Energy Calculation (Hourly)

```python
def calculate_shared_energy_hourly(hour_data):
    """
    For each hour, GSE calculates shared energy as:
    MIN(Total Production, Total Consumption)
    """
    total_production = sum(plant.production_kwh for plant in hour_data.plants)
    total_consumption = sum(member.consumption_kwh for member in hour_data.members)

    shared_energy_kwh = min(total_production, total_consumption)

    return {
        'timestamp': hour_data.timestamp,
        'total_production_kwh': total_production,
        'total_consumption_kwh': total_consumption,
        'shared_energy_kwh': shared_energy_kwh,
        'grid_export_kwh': max(0, total_production - shared_energy_kwh),
        'grid_import_kwh': max(0, total_consumption - shared_energy_kwh)
    }
```

#### 2. TCEC Incentive Calculation

```python
def calculate_tcec_incentive(cer, shared_energy_kwh, timestamp):
    """
    TCEC = Tariffa premio Energia Condivisa
    Range: 60-120 €/MWh based on plant size and hourly zonal price
    Contract duration: 20 years
    """
    # Base tariff (varies by plant size)
    if cer.plant_capacity_kw <= 200:
        base_tariff_eur_mwh = 120
    elif cer.plant_capacity_kw <= 600:
        base_tariff_eur_mwh = 100
    else:
        base_tariff_eur_mwh = 80

    # Regional bonus
    regional_bonus = get_regional_bonus(cer.region)
    # Northern Italy: +10 €/MWh
    # Central Italy: +4 €/MWh
    # Southern Italy: 0

    # Variable component (based on zonal price)
    zonal_price = get_zonal_price(cer.zone, timestamp)
    variable_component = calculate_variable_component(zonal_price)

    total_tariff_eur_mwh = base_tariff_eur_mwh + regional_bonus + variable_component

    incentive_eur = (shared_energy_kwh / 1000) * total_tariff_eur_mwh

    return incentive_eur

def get_regional_bonus(region):
    """Regional bonuses as per GSE rules"""
    northern_regions = ['Emilia-Romagna', 'Friuli-Venezia Giulia', 'Liguria',
                       'Lombardia', 'Piemonte', 'Trentino-Alto Adige',
                       'Valle d\'Aosta', 'Veneto']
    central_regions = ['Lazio', 'Marche', 'Toscana', 'Umbria', 'Abruzzo']

    if region in northern_regions:
        return 10.0
    elif region in central_regions:
        return 4.0
    else:
        return 0.0
```

#### 3. ARERA Valorization

```python
def calculate_arera_valorization(shared_energy_kwh):
    """
    ARERA valorization for self-consumed energy
    Approximately 8 €/MWh (updates annually)
    """
    ARERA_RATE_2025 = 8.48  # €/MWh (based on 2023 rate, adjusted)

    valorization_eur = (shared_energy_kwh / 1000) * ARERA_RATE_2025

    return valorization_eur
```

#### 4. Total Member Benefit

```python
def calculate_member_benefit(member, shared_energy_allocation_kwh, timestamp):
    """
    Total benefit = TCEC incentive + ARERA valorization + Energy savings
    """
    # Incentive portion
    tcec_incentive = calculate_tcec_incentive(member.cer, shared_energy_allocation_kwh, timestamp)
    arera_valor = calculate_arera_valorization(shared_energy_allocation_kwh)

    # Energy cost savings (avoided purchase from grid)
    grid_price_eur_kwh = 0.30  # Average retail price
    energy_savings = shared_energy_allocation_kwh * grid_price_eur_kwh

    total_benefit_eur = tcec_incentive + arera_valor + energy_savings

    return {
        'tcec_incentive_eur': tcec_incentive,
        'arera_valorization_eur': arera_valor,
        'energy_savings_eur': energy_savings,
        'total_benefit_eur': total_benefit_eur
    }
```

### Distribution Formulas

Support multiple allocation methods:

#### Method 1: Equal Share
```python
def distribute_equal_share(total_incentive, members):
    """Simple equal distribution"""
    per_member = total_incentive / len(members)
    return {member.id: per_member for member in members}
```

#### Method 2: Consumption-Based
```python
def distribute_by_consumption(total_incentive, members, hourly_data):
    """Proportional to consumption"""
    total_consumption = sum(m.consumption_kwh for m in hourly_data.members)

    distribution = {}
    for member in members:
        member_consumption = hourly_data.get_member_consumption(member.id)
        share = (member_consumption / total_consumption) if total_consumption > 0 else 0
        distribution[member.id] = total_incentive * share

    return distribution
```

#### Method 3: Production-Based
```python
def distribute_by_production(total_incentive, members, producers):
    """Priority to producers"""
    # 60% to producers, 40% to consumers
    producer_pool = total_incentive * 0.6
    consumer_pool = total_incentive * 0.4

    distribution = {}

    # Distribute producer pool
    total_production = sum(p.production_kwh for p in producers)
    for producer in producers:
        share = producer.production_kwh / total_production
        distribution[producer.member_id] = producer_pool * share

    # Distribute consumer pool equally
    consumers = [m for m in members if m.id not in [p.member_id for p in producers]]
    per_consumer = consumer_pool / len(consumers)
    for consumer in consumers:
        distribution[consumer.id] = distribution.get(consumer.id, 0) + per_consumer

    return distribution
```

#### Method 4: Shapley Value (Game Theory)
```python
def distribute_shapley_value(total_incentive, members, contribution_matrix):
    """
    Fair distribution based on marginal contribution
    More complex but mathematically fair
    """
    from itertools import combinations, permutations

    shapley_values = {}
    n = len(members)

    for member in members:
        marginal_contributions = []

        # Calculate marginal contribution in all possible coalitions
        for size in range(n):
            for coalition in combinations([m for m in members if m.id != member.id], size):
                # Value with member
                with_member = calculate_coalition_value(coalition + [member])
                # Value without member
                without_member = calculate_coalition_value(coalition)
                # Marginal contribution
                marginal = with_member - without_member
                marginal_contributions.append(marginal)

        # Shapley value is average of marginal contributions
        shapley_values[member.id] = sum(marginal_contributions) / len(marginal_contributions)

    # Normalize to total incentive
    total_shapley = sum(shapley_values.values())
    normalized = {
        member_id: (value / total_shapley) * total_incentive
        for member_id, value in shapley_values.items()
    }

    return normalized
```

---

## Member Portal

### User Interface Components

#### 1. Dashboard

```
┌────────────────────────────────────────────────────────┐
│  DASHBOARD - Mario Rossi                    CER Milano │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Current Month Earnings                                │
│  ┌─────────────────────────────────────────────────┐  │
│  │  January 2025                      €45.32       │  │
│  │  ████████████░░░░░░░░░░░░░░  48% of month      │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  Breakdown                                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │  • TCEC Incentive:         €18.20               │  │
│  │  • ARERA Valorization:     €3.12                │  │
│  │  • Energy Savings:         €24.00               │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  Shared Energy This Month                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Your Consumption:  180 kWh                     │  │
│  │  Shared from CER:   120 kWh (67%)               │  │
│  │  From Grid:         60 kWh  (33%)               │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  [View Details] [Download Statement] [History]         │
└────────────────────────────────────────────────────────┘
```

#### 2. Detailed Breakdown

```
┌────────────────────────────────────────────────────────┐
│  JANUARY 2025 - DETAILED BREAKDOWN                     │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Week 1 (Jan 1-7)                            €10.25    │
│  Week 2 (Jan 8-14)                           €11.80    │
│  Week 3 (Jan 15-21)                          €12.10    │
│  Week 4 (Jan 22-28)                          €11.17    │
│                                                         │
│  Daily Energy Flow (Jan 15, 2025)                      │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Hour  Production  Consumption  Shared  Grid    │  │
│  │  00:00     0.5        0.2        0.2    0.3↑    │  │
│  │  01:00     0.4        0.1        0.1    0.3↑    │  │
│  │  ...                                             │  │
│  │  12:00     2.8        1.5        1.5    1.3↑    │  │
│  │  13:00     3.2        1.2        1.2    2.0↑    │  │
│  │  ...                                             │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  [Export CSV] [Export PDF]                             │
└────────────────────────────────────────────────────────┘
```

#### 3. Comparison & Analytics

```
┌────────────────────────────────────────────────────────┐
│  YOUR PERFORMANCE vs CER AVERAGE                       │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Self-Consumption Rate                                 │
│  You: 67%  ██████████████████░░░                       │
│  Avg: 58%  ███████████████░░░░░                        │
│                                                         │
│  Monthly Earnings                                       │
│  You: €45  █████████░░░░░░░░░░                         │
│  Avg: €52  ██████████░░░░░░░░░                         │
│                                                         │
│  Your Rank: 12th / 45 members                          │
│                                                         │
│  💡 Tip: Increase consumption during 10:00-15:00       │
│     to maximize shared energy!                          │
└────────────────────────────────────────────────────────┘
```

### Mobile App Features

- Push notifications for earnings updates
- QR code for member identification
- Offline mode for viewing history
- Dark mode support
- Multi-language (Italian/English)

---

## Database Schema

### New Tables

```sql
-- CER Billing Configuration
CREATE TABLE cer_billing_config (
    id SERIAL PRIMARY KEY,
    cer_id INTEGER NOT NULL REFERENCES cer(id),
    distribution_method VARCHAR(50) NOT NULL, -- 'equal', 'consumption', 'production', 'shapley'
    tcec_base_rate DECIMAL(10,2), -- €/MWh
    regional_bonus DECIMAL(10,2), -- €/MWh
    arera_rate DECIMAL(10,2), -- €/MWh
    calculation_frequency VARCHAR(20), -- 'hourly', 'daily', 'monthly'
    auto_billing_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Energy Measurements (Hourly)
CREATE TABLE cer_energy_measurements (
    id SERIAL PRIMARY KEY,
    cer_id INTEGER NOT NULL REFERENCES cer(id),
    timestamp TIMESTAMP NOT NULL,
    plant_id INTEGER REFERENCES plants(id),
    member_id INTEGER REFERENCES cer_members(id),
    production_kwh DECIMAL(10,3), -- NULL for consumers
    consumption_kwh DECIMAL(10,3), -- NULL for pure producers
    grid_export_kwh DECIMAL(10,3),
    grid_import_kwh DECIMAL(10,3),
    data_source VARCHAR(50), -- 'gse_portal', 'e-distribuzione', 'manual', 'meter'
    import_batch_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_cer_timestamp (cer_id, timestamp),
    INDEX idx_member_timestamp (member_id, timestamp)
);

-- Shared Energy Calculations
CREATE TABLE cer_shared_energy (
    id SERIAL PRIMARY KEY,
    cer_id INTEGER NOT NULL REFERENCES cer(id),
    timestamp TIMESTAMP NOT NULL,
    total_production_kwh DECIMAL(10,3),
    total_consumption_kwh DECIMAL(10,3),
    shared_energy_kwh DECIMAL(10,3),
    grid_export_kwh DECIMAL(10,3),
    grid_import_kwh DECIMAL(10,3),
    calculation_method VARCHAR(50),
    calculated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (cer_id, timestamp)
);

-- Member Incentive Allocations
CREATE TABLE cer_member_incentives (
    id SERIAL PRIMARY KEY,
    cer_id INTEGER NOT NULL REFERENCES cer(id),
    member_id INTEGER NOT NULL REFERENCES cer_members(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    shared_energy_allocated_kwh DECIMAL(10,3),
    tcec_incentive_eur DECIMAL(10,2),
    arera_valorization_eur DECIMAL(10,2),
    energy_savings_eur DECIMAL(10,2),
    total_benefit_eur DECIMAL(10,2),
    distribution_method VARCHAR(50),
    payment_status VARCHAR(20), -- 'pending', 'approved', 'paid', 'cancelled'
    payment_date DATE,
    notes TEXT,
    calculated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_member_period (member_id, period_start, period_end),
    INDEX idx_payment_status (payment_status)
);

-- GSE Portal Integrations
CREATE TABLE gse_portal_sync (
    id SERIAL PRIMARY KEY,
    cer_id INTEGER NOT NULL REFERENCES cer(id),
    sync_type VARCHAR(50), -- 'measurement_import', 'status_check', 'application_submit'
    sync_date TIMESTAMP NOT NULL,
    status VARCHAR(20), -- 'success', 'failed', 'partial'
    records_imported INTEGER,
    error_message TEXT,
    import_file_path VARCHAR(500),
    metadata JSONB,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Member Portal Access
CREATE TABLE cer_member_portal_access (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES cer_members(id),
    user_id INTEGER REFERENCES users(id), -- Link to user account if they sign up
    access_token VARCHAR(255) UNIQUE,
    email VARCHAR(255),
    phone VARCHAR(50),
    last_login TIMESTAMP,
    notification_preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (member_id)
);

-- Billing Statements
CREATE TABLE cer_billing_statements (
    id SERIAL PRIMARY KEY,
    cer_id INTEGER NOT NULL REFERENCES cer(id),
    member_id INTEGER NOT NULL REFERENCES cer_members(id),
    statement_period_start DATE NOT NULL,
    statement_period_end DATE NOT NULL,
    total_shared_energy_kwh DECIMAL(10,3),
    total_incentive_eur DECIMAL(10,2),
    total_savings_eur DECIMAL(10,2),
    statement_pdf_path VARCHAR(500),
    sent_date DATE,
    delivery_status VARCHAR(20), -- 'pending', 'sent', 'viewed', 'downloaded'
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_member_period (member_id, statement_period_start)
);

-- Expectation Management (Forecasting)
CREATE TABLE cer_earnings_forecast (
    id SERIAL PRIMARY KEY,
    cer_id INTEGER NOT NULL REFERENCES cer(id),
    member_id INTEGER REFERENCES cer_members(id), -- NULL for CER-level forecast
    forecast_period VARCHAR(20), -- 'monthly', 'quarterly', 'annual'
    forecast_start_date DATE NOT NULL,
    forecast_end_date DATE NOT NULL,
    expected_shared_energy_kwh DECIMAL(10,3),
    conservative_estimate_eur DECIMAL(10,2),
    realistic_estimate_eur DECIMAL(10,2),
    optimistic_estimate_eur DECIMAL(10,2),
    assumptions JSONB,
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_forecast_period (cer_id, forecast_start_date)
);
```

---

## API Endpoints

### CER Billing Management

```python
# Get CER billing configuration
GET /api/v1/cer/{cer_id}/billing/config
Response: {
    "cer_id": 5,
    "distribution_method": "consumption",
    "tcec_base_rate": 100.0,
    "regional_bonus": 10.0,
    "arera_rate": 8.48,
    "calculation_frequency": "hourly",
    "auto_billing_enabled": true
}

# Update billing configuration
PUT /api/v1/cer/{cer_id}/billing/config
Request: {
    "distribution_method": "shapley",
    "auto_billing_enabled": true
}

# Import energy measurements
POST /api/v1/cer/{cer_id}/billing/measurements/import
Request (multipart/form-data):
    file: measurements.csv
    data_source: "gse_portal"
    period_start: "2025-01-01"
    period_end: "2025-01-31"
Response: {
    "import_id": 123,
    "records_imported": 1440,  # 30 days * 24 hours * 2 (prod+cons)
    "records_failed": 0,
    "status": "success"
}

# Calculate incentives for period
POST /api/v1/cer/{cer_id}/billing/calculate
Request: {
    "period_start": "2025-01-01",
    "period_end": "2025-01-31",
    "distribution_method": "consumption"  # Optional override
}
Response: {
    "calculation_id": 456,
    "period_start": "2025-01-01",
    "period_end": "2025-01-31",
    "total_shared_energy_kwh": 12500.5,
    "total_incentive_eur": 1250.50,
    "members_count": 45,
    "average_per_member_eur": 27.79,
    "status": "completed"
}

# Get member incentives
GET /api/v1/cer/{cer_id}/members/{member_id}/incentives?period_start=2025-01-01&period_end=2025-01-31
Response: {
    "member_id": 10,
    "member_name": "Mario Rossi",
    "period_start": "2025-01-01",
    "period_end": "2025-01-31",
    "shared_energy_allocated_kwh": 180.5,
    "tcec_incentive_eur": 18.20,
    "arera_valorization_eur": 1.53,
    "energy_savings_eur": 54.15,
    "total_benefit_eur": 73.88,
    "payment_status": "pending"
}

# Generate billing statement
POST /api/v1/cer/{cer_id}/members/{member_id}/statement
Request: {
    "period_start": "2025-01-01",
    "period_end": "2025-01-31",
    "format": "pdf",  # or "csv", "excel"
    "send_email": true
}
Response: {
    "statement_id": 789,
    "pdf_url": "/downloads/statements/statement_789.pdf",
    "sent_to": "mario.rossi@email.com",
    "delivery_status": "sent"
}

# Get earnings forecast
GET /api/v1/cer/{cer_id}/members/{member_id}/forecast?period=monthly
Response: {
    "member_id": 10,
    "forecast_period": "monthly",
    "current_month": "2025-02",
    "conservative_estimate_eur": 45.00,
    "realistic_estimate_eur": 52.00,
    "optimistic_estimate_eur": 62.00,
    "assumptions": {
        "avg_consumption_kwh": 200,
        "avg_shared_percentage": 65,
        "weather_factor": "normal"
    }
}

# Dashboard data for member portal
GET /api/v1/cer/{cer_id}/members/{member_id}/dashboard
Response: {
    "current_month": {
        "earnings_to_date_eur": 45.32,
        "days_elapsed": 15,
        "days_total": 31,
        "progress_percentage": 48,
        "shared_energy_kwh": 120.5,
        "self_consumption_rate": 67
    },
    "last_month": {
        "total_earnings_eur": 52.10,
        "shared_energy_kwh": 180.2
    },
    "year_to_date": {
        "total_earnings_eur": 97.42,
        "avg_monthly_eur": 48.71
    },
    "rank": {
        "position": 12,
        "total_members": 45,
        "percentile": 73
    }
}
```

---

## Implementation Plan

### Phase 1A: Core Functionality (Week 1-4)

**Week 1-2: Database & Backend**
- [ ] Create database schema
- [ ] Implement calculation engine
- [ ] Build distribution formulas (all 4 methods)
- [ ] Create API endpoints
- [ ] Unit tests for calculations

**Week 3-4: Data Import & Processing**
- [ ] CSV/Excel import functionality
- [ ] GSE data parser
- [ ] E-Distribuzione data parser
- [ ] Batch processing for large datasets
- [ ] Error handling and validation

### Phase 1B: Member Portal (Week 5-8)

**Week 5-6: Frontend Development**
- [ ] Dashboard UI
- [ ] Detailed breakdown views
- [ ] Charts and visualizations
- [ ] Mobile responsive design
- [ ] PDF statement generation

**Week 7-8: Integration & Testing**
- [ ] Connect frontend to backend APIs
- [ ] User authentication
- [ ] Email notifications
- [ ] End-to-end testing
- [ ] Performance optimization

### Phase 1C: GSE Integration (Week 9-10)

**Week 9: Manual Integration**
- [ ] Documentation for GSE data export
- [ ] Import wizard UI
- [ ] Status tracking dashboard
- [ ] GSE portal mapping guide

**Week 10: Automation Prep**
- [ ] Research web scraping feasibility
- [ ] Legal compliance check
- [ ] Selenium/Playwright setup (if approved)
- [ ] Automated login prototype

### Phase 1D: Launch (Week 11-12)

**Week 11: Pilot Testing**
- [ ] Select 3-5 pilot CERs
- [ ] Import historical data
- [ ] Run calculations
- [ ] Validate against GSE results
- [ ] Gather feedback

**Week 12: Production Launch**
- [ ] Deploy to production
- [ ] Onboard first 20 CERs
- [ ] Training materials
- [ ] Support documentation
- [ ] Marketing launch

---

## Testing Strategy

### Unit Tests

```python
def test_shared_energy_calculation():
    """Test hourly shared energy calculation"""
    hour_data = {
        'total_production': 100,
        'total_consumption': 80
    }
    result = calculate_shared_energy_hourly(hour_data)
    assert result['shared_energy_kwh'] == 80
    assert result['grid_export_kwh'] == 20

def test_tcec_incentive():
    """Test TCEC incentive calculation"""
    cer = create_test_cer(capacity_kw=150, region='Lombardia')
    incentive = calculate_tcec_incentive(cer, shared_energy_kwh=100, timestamp='2025-01-15 12:00')
    assert incentive > 10.0  # 100 kWh * (120 + 10 regional) = 13 EUR

def test_distribution_methods():
    """Test all distribution methods produce correct totals"""
    total_incentive = 1000.0
    members = create_test_members(count=10)

    for method in ['equal', 'consumption', 'production', 'shapley']:
        distribution = apply_distribution(method, total_incentive, members)
        assert sum(distribution.values()) == pytest.approx(total_incentive, rel=0.01)
```

### Integration Tests

```python
def test_full_billing_cycle():
    """Test complete billing cycle from import to statement"""
    # 1. Import measurements
    import_result = import_measurements_csv('test_data.csv', cer_id=1)
    assert import_result['status'] == 'success'

    # 2. Calculate shared energy
    shared = calculate_shared_energy(cer_id=1, period='2025-01')
    assert shared['total_shared_energy_kwh'] > 0

    # 3. Distribute incentives
    distribution = distribute_incentives(cer_id=1, method='consumption')
    assert len(distribution) == get_member_count(cer_id=1)

    # 4. Generate statements
    for member_id in distribution.keys():
        statement = generate_statement(cer_id=1, member_id=member_id, period='2025-01')
        assert statement['pdf_url'] is not None
```

### User Acceptance Testing

- [ ] CER administrators can import GSE data
- [ ] Calculations match GSE results (within 1% tolerance)
- [ ] Members can view earnings in portal
- [ ] Statements are accurate and readable
- [ ] Forecasts are within 20% of actual results

---

## Success Metrics

### Technical KPIs

- **Calculation Accuracy:** 99%+ match with GSE
- **Import Speed:** < 5 seconds for 1 month of hourly data (720 records)
- **API Response Time:** < 200ms for dashboard
- **Portal Load Time:** < 2 seconds
- **Uptime:** 99.5%

### Business KPIs

- **CER Adoption:** 20 CERs in first 3 months
- **Member Satisfaction:** 4.5/5 average rating
- **Time Savings:** 80% reduction in admin time
- **Expectation Gap:** Reduce from 100% difference to <20%
- **Churn Rate:** <5% CER cancellation rate

---

## Revenue Model

### Pricing Structure

```
Setup Fee: €2,000 - €5,000 per CER
- Initial configuration
- Historical data import
- Admin training
- Member portal setup

Monthly Subscription: €200 - €800 per CER
Based on member count:
- 1-20 members: €200/month
- 21-50 members: €400/month
- 51-100 members: €600/month
- 100+ members: €800/month

Transaction Fee: 1-2% of incentive distributed
- Optional add-on
- Deducted from incentive before distribution
- Or billed separately to CER

Premium Features: €5-10/month per member
- Mobile app access
- Advanced analytics
- Custom reports
- SMS notifications
```

### Revenue Projections

```
Year 1 (20 CERs, avg 40 members each):
- Setup fees: €60,000
- Subscriptions: €96,000 (20 * €400 * 12)
- Transaction fees: €19,200 (assuming 2% of €80K avg monthly incentives)
Total: €175,200

Year 2 (60 CERs):
- Setup fees: €120,000
- Subscriptions: €288,000
- Transaction fees: €57,600
Total: €465,600

Year 3 (150 CERs):
- Setup fees: €270,000
- Subscriptions: €720,000
- Transaction fees: €144,000
Total: €1,134,000
```

---

## Risk Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| GSE changes formulas | Medium | High | Version control on formulas, quick update process |
| No official API | High | Medium | Web scraping backup, manual import option |
| Data quality issues | Medium | Medium | Robust validation, error reporting |
| Performance with large CERs | Low | Medium | Database optimization, caching |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Slow CER adoption | Medium | High | Focus on operational CERs first, pilot program |
| Regulatory changes | Medium | High | Modular design, legal advisory |
| Competition | Low | Medium | First-mover advantage, feature richness |
| Member data privacy | Low | High | GDPR compliance, security audit |

---

## Next Steps

1. **Validate with Customers (Week 0)**
   - Interview 10 CER administrators
   - Show wireframes and pricing
   - Get commitment for pilot

2. **Technical Setup (Week 1)**
   - Set up development environment
   - Create database schemas
   - Initialize repositories

3. **Development Sprint (Week 2-10)**
   - Follow implementation plan
   - Weekly demos to stakeholders
   - Iterative feedback

4. **Pilot Launch (Week 11-12)**
   - Onboard 3-5 CERs
   - Real-world testing
   - Refinement

5. **Production Launch (Week 13+)**
   - Marketing campaign
   - Onboarding at scale
   - Support and iteration

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Owner:** SentricS2 Product Team
**Status:** Ready for Development
