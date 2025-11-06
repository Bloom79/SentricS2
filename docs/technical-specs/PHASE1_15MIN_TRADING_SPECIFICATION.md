# Phase 1 - 15-Minute Trading Module - Technical Specification

**Version:** 1.0
**Date:** January 2025
**Status:** Ready for Implementation
**Priority:** HIGHEST (TIDE mandatory January 2025)

---

## Executive Summary

The 15-Minute Trading Module enables plant operators to optimize revenue in Italy's new TIDE (Testo Integrato del Dispacciamento Elettrico) market structure that began January 1, 2025. The shift from hourly to 15-minute settlement intervals creates massive arbitrage opportunities, especially with emerging negative prices.

**Market Opportunity:**
- TIDE reform MANDATORY since January 1, 2025
- 96 daily auctions (vs 24 previously)
- Negative prices emerging (Sardinia, Sicily)
- Most operators unprepared
- Revenue potential: €1.2-6M annually

---

## Table of Contents

1. [TIDE Reform Overview](#tide-reform-overview)
2. [Business Requirements](#business-requirements)
3. [Technical Architecture](#technical-architecture)
4. [GME/Terna Integration](#gme-terna-integration)
5. [Optimization Engine](#optimization-engine)
6. [Database Schema](#database-schema)
7. [API Endpoints](#api-endpoints)
8. [Implementation Plan](#implementation-plan)

---

## TIDE Reform Overview

### What Changed on January 1, 2025

**Before TIDE:**
- Hourly settlement periods (24 periods/day)
- Hourly PUN (Prezzo Unico Nazionale)
- Fixed zonal prices per hour
- Limited flexibility opportunities

**After TIDE:**
- **15-minute settlement periods (96 periods/day)**
- **Quarterly PUN updates**
- **Dynamic zonal pricing**
- **Increased volatility = more opportunities**

### Key Market Changes

```
Settlement Granularity:
1 Hour (60 min) → 4 Quarters (15 min each)

Daily Auctions:
24 hourly auctions → 96 quarterly auctions

Price Updates:
24 times/day → 96 times/day

Market Time Unit (MTU):
Hourly → Quarterly (15-minute)
```

### Impact on Renewable Operators

1. **More Price Volatility**
   - Prices can change 4x per hour
   - Opportunity for arbitrage
   - Risk of negative prices

2. **Curtailment Strategies**
   - Stop production during negative prices
   - Resume when profitable
   - Automated decision-making needed

3. **Load Shifting**
   - Move consumption to low-price periods
   - Charge batteries during negative prices
   - Sell during high-price periods

4. **Intraday Trading**
   - Continuous trading in 15-min blocks
   - Adjust positions based on forecasts
   - Balance portfolio across plants

---

## Business Requirements

### Core Functionality

1. **Real-Time Price Monitoring**
   - Monitor GME prices every 15 minutes
   - Track 7 zonal prices (Italy zones)
   - Alert on negative prices
   - Historical price analysis

2. **Production Optimization**
   - Automatic curtailment recommendations
   - Resume production signals
   - Economic dispatch across portfolio
   - Weather-based forecasting

3. **Automated Trading**
   - Day-ahead market bidding
   - Intraday position adjustment
   - Portfolio balancing
   - Risk management

4. **Negative Price Management**
   - Automatic alerts
   - Curtailment triggers
   - Cost-benefit analysis
   - PPA compliance checking

### User Stories

**As a plant operator, I want to:**
- See current and forecasted 15-minute prices
- Get alerts when prices go negative
- Automatically curtail production to avoid losses
- Optimize dispatch across my portfolio
- Track earnings from trading vs fixed PPA

**As a portfolio manager, I want to:**
- View all plants on one dashboard
- Optimize production across all sites
- Balance long/short positions
- Forecast revenues under different scenarios
- Minimize imbalance costs

---

## Technical Architecture

### System Components

```
┌──────────────────────────────────────────────────────────────┐
│              15-Minute Trading Module                         │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │ Price Feed   │───▶│ Optimization │───▶│  Trading     │   │
│  │ Integration  │    │    Engine    │    │  Execution   │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│         │                    │                    │           │
│         ▼                    ▼                    ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │ Weather      │    │ Production   │    │   Position   │   │
│  │ Forecasting  │    │ Forecasting  │    │  Management  │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│         │                    │                    │           │
│         └────────────────────┴────────────────────┘           │
│                              │                                │
│                    ┌─────────▼─────────┐                      │
│                    │   Database        │                      │
│                    │   - Prices        │                      │
│                    │   - Forecasts     │                      │
│                    │   - Positions     │                      │
│                    │   - Trades        │                      │
│                    └───────────────────┘                      │
└──────────────────────────────────────────────────────────────┘

External Integrations:
├── GME (Gestore Mercati Energetici) - Price data
├── Terna - Grid data & constraints
├── Weather APIs - Production forecasting
└── Plant SCADA - Real-time production
```

---

## GME/Terna Integration

### GME API Integration

Based on research, GME provides official API service since October 2025:

**Endpoint:** `https://api.mercatoelettrico.org/request/api/v1/`

**Authentication:**
```python
POST /api/v1/Auth
Request: {
    "username": "your_username",
    "password": "your_password"
}
Response: {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600
}
```

**Get 15-Minute Prices:**
```python
POST /api/v1/RequestData
Headers: {
    "Authorization": "Bearer {token}"
}
Request: {
    "market": "MGP",  # Mercato del Giorno Prima (Day-Ahead)
    "date": "2025-01-15",
    "data_type": "PrezziZonali",  # Zonal Prices
    "format": "json"
}
Response: {
    "data": [
        {
            "timestamp": "2025-01-15T00:00:00",
            "quarter": 1,  # First 15-min of hour
            "zone": "NORD",
            "price_eur_mwh": 85.32
        },
        {
            "timestamp": "2025-01-15T00:15:00",
            "quarter": 2,
            "zone": "NORD",
            "price_eur_mwh": 82.10
        },
        // ... 96 quarters per day, 7 zones
    ]
}
```

### Italian Market Zones

```python
ITALIAN_ZONES = {
    'NORD': 'Northern Italy',
    'CNOR': 'North-Central Italy',
    'CSUD': 'South-Central Italy',
    'SUD': 'Southern Italy',
    'CALA': 'Calabria',
    'SICI': 'Sicily',
    'SARD': 'Sardinia'
}
```

### Terna Data Portal

**URL:** `https://dati.terna.it/`

**Available Data:**
- Load (Fabbisogno elettrico)
- Generation (Generazione Energia)
- Transmission (Trasmissione)
- Fees (Corrispettivi)
- Outages (Fuori Servizio)

**Data Access:**
- REST API available
- JSON format
- Real-time and historical
- Download center for bulk data

### Price Feed Implementation

```python
class GMEPriceFeed:
    """Real-time 15-minute price feed from GME"""

    def __init__(self, username, password):
        self.api_url = "https://api.mercatoelettrico.org/request/api/v1/"
        self.username = username
        self.password = password
        self.token = None
        self.token_expires = None

    async def authenticate(self):
        """Get authentication token"""
        response = await self.post("/Auth", {
            "username": self.username,
            "password": self.password
        })
        self.token = response['token']
        self.token_expires = datetime.now() + timedelta(seconds=response['expires_in'])

    async def get_current_prices(self):
        """Get current 15-minute prices for all zones"""
        if not self.token or datetime.now() >= self.token_expires:
            await self.authenticate()

        today = datetime.now().date()
        response = await self.post("/RequestData", {
            "market": "MGP",
            "date": today.isoformat(),
            "data_type": "PrezziZonali",
            "format": "json"
        }, headers={"Authorization": f"Bearer {self.token}"})

        # Extract current quarter
        current_time = datetime.now()
        current_quarter = (current_time.hour * 4) + (current_time.minute // 15)

        current_prices = {}
        for record in response['data']:
            if record['quarter'] == current_quarter:
                current_prices[record['zone']] = record['price_eur_mwh']

        return current_prices

    async def get_day_ahead_prices(self, date):
        """Get all 96 quarterly prices for a specific date"""
        response = await self.post("/RequestData", {
            "market": "MGP",
            "date": date.isoformat(),
            "data_type": "PrezziZonali",
            "format": "json"
        })

        # Organize by hour and quarter
        prices_by_zone = {}
        for record in response['data']:
            zone = record['zone']
            if zone not in prices_by_zone:
                prices_by_zone[zone] = []
            prices_by_zone[zone].append({
                'timestamp': record['timestamp'],
                'quarter': record['quarter'],
                'price_eur_mwh': record['price_eur_mwh']
            })

        return prices_by_zone

    async def subscribe_realtime(self, callback):
        """Subscribe to real-time price updates (polling-based)"""
        while True:
            try:
                prices = await self.get_current_prices()
                await callback(prices)
            except Exception as e:
                logger.error(f"Price feed error: {e}")

            # Wait until next 15-minute boundary
            now = datetime.now()
            next_quarter = (now.minute // 15 + 1) * 15
            if next_quarter >= 60:
                next_time = now.replace(hour=now.hour+1, minute=0, second=0)
            else:
                next_time = now.replace(minute=next_quarter, second=0)

            sleep_seconds = (next_time - now).total_seconds()
            await asyncio.sleep(sleep_seconds)
```

---

## Optimization Engine

### Price-Based Decision Making

```python
class PriceOptimizer:
    """Optimize plant operations based on 15-minute prices"""

    def __init__(self, plant, price_feed):
        self.plant = plant
        self.price_feed = price_feed

    async def should_curtail(self, current_price, forecast_production_kw):
        """
        Decide if plant should curtail production

        Curtail if:
        1. Price is negative
        2. Price below variable cost
        3. PPA allows curtailment
        """
        # Check if price is negative
        if current_price < 0:
            logger.info(f"Negative price detected: {current_price} EUR/MWh")
            return True, f"Negative price: {current_price} EUR/MWh"

        # Check if below variable operating cost
        variable_cost = self.plant.variable_cost_eur_mwh  # e.g., 5 EUR/MWh
        if current_price < variable_cost:
            logger.info(f"Price {current_price} below variable cost {variable_cost}")
            return True, f"Price below cost: {current_price} < {variable_cost}"

        # Check PPA constraints
        if self.plant.has_ppa:
            if not self.plant.ppa_allows_curtailment:
                return False, "PPA does not allow curtailment"

            # Check if PPA price is better
            ppa_price = self.plant.ppa_price_eur_mwh
            if ppa_price > current_price:
                # Still better to sell to grid at PPA price
                return False, f"PPA price {ppa_price} better than market {current_price}"

        return False, "No curtailment needed"

    async def optimize_hourly_dispatch(self, hour_start, forecasts):
        """
        Optimize dispatch across 4 x 15-minute quarters

        Given: Price forecast for next 4 quarters
        Decide: Production level for each quarter
        """
        quarters = []

        for i, quarter_forecast in enumerate(forecasts[:4]):
            timestamp = hour_start + timedelta(minutes=i*15)
            price = quarter_forecast['price_eur_mwh']
            expected_production = quarter_forecast['production_kw']

            # Decision
            curtail, reason = await self.should_curtail(price, expected_production)

            quarter_plan = {
                'timestamp': timestamp,
                'quarter': i + 1,
                'forecasted_price': price,
                'forecasted_production_kw': expected_production,
                'curtail': curtail,
                'target_production_kw': 0 if curtail else expected_production,
                'expected_revenue_eur': 0 if curtail else (expected_production * price / 1000),
                'reason': reason
            }

            quarters.append(quarter_plan)

        return quarters

    async def calculate_arbitrage_opportunity(self, day_ahead_prices, battery_capacity_kwh):
        """
        Calculate battery arbitrage opportunities

        Strategy:
        - Charge during low/negative prices
        - Discharge during high prices
        """
        if not battery_capacity_kwh:
            return []

        # Sort quarters by price
        sorted_quarters = sorted(day_ahead_prices, key=lambda x: x['price_eur_mwh'])

        opportunities = []

        # Identify charging opportunities (lowest 25% of prices)
        num_quarters = len(sorted_quarters)
        charge_quarters = sorted_quarters[:num_quarters // 4]

        # Identify discharging opportunities (highest 25% of prices)
        discharge_quarters = sorted_quarters[-num_quarters // 4:]

        # Calculate potential profit
        avg_charge_price = sum(q['price_eur_mwh'] for q in charge_quarters) / len(charge_quarters)
        avg_discharge_price = sum(q['price_eur_mwh'] for q in discharge_quarters) / len(discharge_quarters)

        # Account for efficiency losses (round-trip efficiency ~85%)
        efficiency = 0.85
        spread = (avg_discharge_price - avg_charge_price) * efficiency

        if spread > 0:
            # Calculate daily revenue
            cycles = len(charge_quarters) / 4  # How many full charge/discharge cycles
            revenue_per_cycle = battery_capacity_kwh * spread / 1000  # EUR
            daily_revenue = cycles * revenue_per_cycle

            opportunities.append({
                'date': day_ahead_prices[0]['timestamp'].date(),
                'strategy': 'arbitrage',
                'charge_quarters': [q['quarter'] for q in charge_quarters],
                'discharge_quarters': [q['quarter'] for q in discharge_quarters],
                'avg_buy_price': avg_charge_price,
                'avg_sell_price': avg_discharge_price,
                'spread_eur_mwh': spread,
                'daily_revenue_eur': daily_revenue,
                'cycles': cycles
            })

        return opportunities
```

### Negative Price Management

```python
class NegativePriceManager:
    """Handle negative price scenarios"""

    def __init__(self, alert_service):
        self.alert_service = alert_service

    async def monitor_negative_prices(self, price_feed):
        """Monitor and alert on negative prices"""

        async def price_callback(prices):
            for zone, price in prices.items():
                if price < 0:
                    await self.handle_negative_price(zone, price)

        await price_feed.subscribe_realtime(price_callback)

    async def handle_negative_price(self, zone, price):
        """Handle negative price event"""

        # Find affected plants
        affected_plants = Plant.query.filter_by(zone=zone).all()

        for plant in affected_plants:
            # Send alert
            await self.alert_service.send_alert(
                plant_id=plant.id,
                type='negative_price',
                severity='high',
                message=f"Negative price in {zone}: {price} EUR/MWh. Consider curtailment.",
                data={
                    'zone': zone,
                    'price_eur_mwh': price,
                    'timestamp': datetime.now().isoformat()
                }
            )

            # Auto-curtail if enabled
            if plant.auto_curtail_on_negative:
                await self.curtail_plant(plant, reason=f"Negative price: {price}")

    async def curtail_plant(self, plant, reason):
        """Send curtailment command to plant"""

        # Log decision
        logger.info(f"Curtailing plant {plant.id}: {reason}")

        # Send command to SCADA
        if plant.scada_endpoint:
            await plant.scada_client.set_production_target(0)

        # Record in database
        CurtailmentEvent.create(
            plant_id=plant.id,
            timestamp=datetime.now(),
            reason=reason,
            duration_minutes=15,  # For one quarter
            avoided_loss_eur=self.calculate_avoided_loss(plant, price)
        )

    def calculate_avoided_loss(self, plant, negative_price):
        """Calculate money saved by curtailing"""
        expected_production_kwh = plant.current_production_forecast_kw * 0.25  # 15 minutes
        avoided_loss = expected_production_kwh * abs(negative_price) / 1000
        return avoided_loss
```

### Portfolio Optimization

```python
class PortfolioOptimizer:
    """Optimize dispatch across multiple plants"""

    def __init__(self, plants, price_feed):
        self.plants = plants
        self.price_feed = price_feed

    async def optimize_portfolio(self, timestamp):
        """
        Economic dispatch across all plants

        Objective: Maximize total portfolio revenue
        Constraints:
        - PPA obligations
        - Grid constraints
        - Battery state of charge
        - Weather forecasts
        """

        # Get prices for all zones
        prices = await self.price_feed.get_current_prices()

        # Get production forecasts
        forecasts = {
            plant.id: await plant.get_production_forecast(timestamp)
            for plant in self.plants
        }

        decisions = []

        for plant in self.plants:
            zone_price = prices.get(plant.zone, 0)
            forecast_kw = forecasts[plant.id]

            # Optimization decision
            if zone_price < 0 and plant.can_curtail:
                # Curtail this plant
                target_kw = 0
                action = 'curtail'
            elif plant.has_battery and zone_price < 20:  # Low price - charge battery
                target_kw = forecast_kw
                battery_action = 'charge'
                action = 'produce_and_charge'
            elif plant.has_battery and zone_price > 100:  # High price - discharge battery
                target_kw = forecast_kw + plant.battery.max_discharge_kw
                battery_action = 'discharge'
                action = 'produce_and_discharge'
            else:
                # Normal operation
                target_kw = forecast_kw
                action = 'normal'

            decisions.append({
                'plant_id': plant.id,
                'timestamp': timestamp,
                'zone': plant.zone,
                'price_eur_mwh': zone_price,
                'forecast_kw': forecast_kw,
                'target_kw': target_kw,
                'action': action,
                'expected_revenue_eur': self.calculate_revenue(target_kw, zone_price)
            })

        return decisions

    def calculate_revenue(self, production_kw, price_eur_mwh):
        """Calculate 15-minute revenue"""
        production_kwh = production_kw * 0.25  # 15 minutes = 0.25 hours
        revenue_eur = (production_kwh / 1000) * price_eur_mwh
        return revenue_eur
```

---

## Database Schema

### New Tables

```sql
-- Market Prices (15-minute granularity)
CREATE TABLE market_prices_15min (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    quarter INTEGER NOT NULL,  -- 1-96 (96 quarters per day)
    zone VARCHAR(10) NOT NULL,  -- 'NORD', 'SICI', 'SARD', etc.
    price_eur_mwh DECIMAL(10,3) NOT NULL,
    pun DECIMAL(10,3),  -- Prezzo Unico Nazionale
    market_type VARCHAR(20),  -- 'MGP', 'MI', 'MSD'
    is_negative BOOLEAN DEFAULT false,
    data_source VARCHAR(50),  -- 'gme_api', 'manual'
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (timestamp, quarter, zone, market_type),
    INDEX idx_timestamp_zone (timestamp, zone),
    INDEX idx_negative_prices (is_negative, timestamp) WHERE is_negative = true
);

-- Price Alerts
CREATE TABLE price_alerts (
    id SERIAL PRIMARY KEY,
    plant_id INTEGER REFERENCES plants(id),
    alert_type VARCHAR(50),  -- 'negative_price', 'high_price', 'price_spike'
    threshold_value DECIMAL(10,2),
    zone VARCHAR(10),
    triggered_at TIMESTAMP NOT NULL,
    price_eur_mwh DECIMAL(10,3),
    alert_sent BOOLEAN DEFAULT false,
    alert_method VARCHAR(50),  -- 'email', 'sms', 'push', 'webhook'
    acknowledged BOOLEAN DEFAULT false,
    acknowledged_at TIMESTAMP,
    acknowledged_by INTEGER REFERENCES users(id),

    INDEX idx_plant_triggered (plant_id, triggered_at)
);

-- Curtailment Events
CREATE TABLE curtailment_events (
    id SERIAL PRIMARY KEY,
    plant_id INTEGER NOT NULL REFERENCES plants(id),
    start_timestamp TIMESTAMP NOT NULL,
    end_timestamp TIMESTAMP,
    duration_minutes INTEGER,
    reason VARCHAR(200),  -- 'negative_price', 'grid_constraint', 'manual'
    trigger_type VARCHAR(50),  -- 'automatic', 'manual', 'scheduled'
    forecasted_production_kwh DECIMAL(10,3),
    actual_curtailed_kwh DECIMAL(10,3),
    market_price_eur_mwh DECIMAL(10,3),
    avoided_loss_eur DECIMAL(10,2),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_plant_timestamp (plant_id, start_timestamp)
);

-- Trading Decisions
CREATE TABLE trading_decisions_15min (
    id SERIAL PRIMARY KEY,
    plant_id INTEGER NOT NULL REFERENCES plants(id),
    timestamp TIMESTAMP NOT NULL,
    quarter INTEGER NOT NULL,
    decision_type VARCHAR(50),  -- 'curtail', 'normal', 'charge', 'discharge'
    market_price_eur_mwh DECIMAL(10,3),
    forecasted_production_kw DECIMAL(10,2),
    target_production_kw DECIMAL(10,2),
    actual_production_kw DECIMAL(10,2),
    revenue_eur DECIMAL(10,2),
    decision_reason TEXT,
    auto_executed BOOLEAN DEFAULT false,
    executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_plant_timestamp (plant_id, timestamp)
);

-- Intraday Positions
CREATE TABLE intraday_positions (
    id SERIAL PRIMARY KEY,
    plant_id INTEGER NOT NULL REFERENCES plants(id),
    portfolio_id INTEGER,  -- For multi-plant portfolios
    trade_date DATE NOT NULL,
    quarter INTEGER NOT NULL,
    position_type VARCHAR(20),  -- 'long', 'short', 'neutral'
    quantity_mwh DECIMAL(10,3),
    entry_price_eur_mwh DECIMAL(10,3),
    current_price_eur_mwh DECIMAL(10,3),
    unrealized_pnl_eur DECIMAL(10,2),
    status VARCHAR(20),  -- 'open', 'closed', 'partially_closed'
    closed_at TIMESTAMP,
    exit_price_eur_mwh DECIMAL(10,3),
    realized_pnl_eur DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_plant_date (plant_id, trade_date),
    INDEX idx_status (status)
);

-- Optimization Results
CREATE TABLE optimization_results (
    id SERIAL PRIMARY KEY,
    optimization_run_id UUID NOT NULL,
    portfolio_id INTEGER,
    optimization_timestamp TIMESTAMP NOT NULL,
    horizon_start TIMESTAMP NOT NULL,
    horizon_end TIMESTAMP NOT NULL,
    objective_value DECIMAL(15,2),  -- Total expected revenue
    optimization_time_seconds DECIMAL(10,3),
    algorithm_used VARCHAR(100),
    constraints_count INTEGER,
    variables_count INTEGER,
    plant_decisions JSONB,  -- Array of plant-level decisions
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_portfolio_timestamp (portfolio_id, optimization_timestamp)
);

-- Weather Forecasts (for production forecasting)
CREATE TABLE weather_forecasts (
    id SERIAL PRIMARY KEY,
    plant_id INTEGER NOT NULL REFERENCES plants(id),
    forecast_timestamp TIMESTAMP NOT NULL,
    forecast_horizon_minutes INTEGER,  -- 15, 30, 60, etc.
    temperature_celsius DECIMAL(5,2),
    cloud_cover_percent DECIMAL(5,2),
    irradiance_w_m2 DECIMAL(8,2),
    wind_speed_m_s DECIMAL(6,2),
    precipitation_mm DECIMAL(6,2),
    forecasted_production_kw DECIMAL(10,2),
    confidence_level DECIMAL(5,2),
    forecast_source VARCHAR(100),  -- 'openweather', 'weatherapi', 'solcast'
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_plant_forecast (plant_id, forecast_timestamp)
);
```

---

## API Endpoints

### Price Monitoring

```python
# Get current 15-minute prices
GET /api/v1/trading/prices/current
Response: {
    "timestamp": "2025-01-15T14:30:00Z",
    "quarter": 59,
    "prices": {
        "NORD": 85.32,
        "CNOR": 87.10,
        "CSUD": 89.50,
        "SUD": 91.20,
        "CALA": 92.80,
        "SICI": -5.20,  # Negative!
        "SARD": -12.50  # Negative!
    },
    "pun": 78.45
}

# Get day-ahead prices
GET /api/v1/trading/prices/day-ahead?date=2025-01-16&zone=NORD
Response: {
    "date": "2025-01-16",
    "zone": "NORD",
    "quarters": [
        {"quarter": 1, "time": "00:00", "price_eur_mwh": 82.10},
        {"quarter": 2, "time": "00:15", "price_eur_mwh": 80.50},
        ...
        {"quarter": 96, "time": "23:45", "price_eur_mwh": 95.30}
    ],
    "statistics": {
        "min_price": 45.20,
        "max_price": 125.80,
        "avg_price": 85.32,
        "negative_quarters": 0
    }
}

# Get price alerts
GET /api/v1/trading/alerts?plant_id=5&status=pending
Response: {
    "alerts": [
        {
            "id": 123,
            "plant_id": 5,
            "alert_type": "negative_price",
            "triggered_at": "2025-01-15T14:30:00Z",
            "price_eur_mwh": -12.50,
            "zone": "SARD",
            "acknowledged": false,
            "recommended_action": "curtail"
        }
    ]
}
```

### Production Optimization

```python
# Get curtailment recommendations
GET /api/v1/trading/plants/{plant_id}/curtailment/recommendations
Response: {
    "plant_id": 5,
    "current_time": "2025-01-15T14:30:00Z",
    "current_price_eur_mwh": -12.50,
    "recommendation": {
        "action": "curtail",
        "reason": "Negative price",
        "duration_minutes": 45,  # Until prices recover
        "expected_savings_eur": 125.50,
        "confidence": 0.95
    },
    "next_4_quarters": [
        {"quarter": 59, "price": -12.50, "action": "curtail"},
        {"quarter": 60, "price": -8.20, "action": "curtail"},
        {"quarter": 61, "price": 5.30, "action": "resume"},
        {"quarter": 62, "price": 15.80, "action": "normal"}
    ]
}

# Execute curtailment
POST /api/v1/trading/plants/{plant_id}/curtailment/execute
Request: {
    "duration_minutes": 15,
    "reason": "negative_price",
    "auto_resume": true
}
Response: {
    "event_id": 456,
    "plant_id": 5,
    "status": "executed",
    "start_time": "2025-01-15T14:30:00Z",
    "end_time": "2025-01-15T14:45:00Z",
    "command_sent": true,
    "scada_response": "OK"
}

# Get optimization results
POST /api/v1/trading/portfolio/optimize
Request: {
    "portfolio_id": 10,
    "horizon_hours": 24,
    "objective": "maximize_revenue",
    "constraints": {
        "respect_ppa": true,
        "max_curtailment_hours": 4
    }
}
Response: {
    "optimization_id": "uuid-123",
    "expected_revenue_eur": 15250.00,
    "baseline_revenue_eur": 14100.00,
    "improvement_eur": 1150.00,
    "improvement_percent": 8.15,
    "decisions": [
        {
            "plant_id": 5,
            "curtailment_quarters": [23, 24, 25],
            "savings_eur": 450.00
        },
        {
            "plant_id": 7,
            "battery_charge_quarters": [30, 31, 32, 33],
            "battery_discharge_quarters": [70, 71, 72, 73],
            "arbitrage_revenue_eur": 700.00
        }
    ]
}
```

### Analytics & Reporting

```python
# Trading performance report
GET /api/v1/trading/plants/{plant_id}/performance?start_date=2025-01-01&end_date=2025-01-31
Response: {
    "plant_id": 5,
    "period": "2025-01",
    "summary": {
        "total_production_mwh": 5250.5,
        "market_revenue_eur": 425000.00,
        "ppa_revenue_eur": 315000.00,  # If applicable
        "total_revenue_eur": 740000.00,
        "curtailed_mwh": 125.5,
        "avoided_losses_eur": 1580.00,
        "negative_price_events": 15
    },
    "by_quarter_analysis": {
        "most_profitable_quarter": {"time": "13:00-13:15", "avg_price": 145.30},
        "least_profitable_quarter": {"time": "03:00-03:15", "avg_price": 32.10},
        "negative_price_quarters": 15
    }
}
```

---

## Implementation Plan

### Week 1-2: Price Feed Integration
- [ ] GME API registration and credentials
- [ ] Implement authentication
- [ ] Build price feed client
- [ ] Database schema for prices
- [ ] Hourly data import (historical)
- [ ] Real-time 15-min updates

### Week 3-4: Optimization Engine
- [ ] Curtailment decision logic
- [ ] Negative price handler
- [ ] Weather forecast integration
- [ ] Production forecasting
- [ ] Simple optimization algorithms
- [ ] Alert system

### Week 5-6: Trading Execution
- [ ] SCADA integration for curtailment
- [ ] Position management
- [ ] Portfolio optimizer
- [ ] Risk management rules
- [ ] PPA compliance checks

### Week 7-8: UI & Reporting
- [ ] Real-time price dashboard
- [ ] Plant optimization UI
- [ ] Alert management UI
- [ ] Performance reports
- [ ] Mobile alerts

### Week 9-10: Testing & Launch
- [ ] Pilot with 3 plants
- [ ] Validate against actual market
- [ ] Tune algorithms
- [ ] Production deployment

---

## Success Metrics

- **Price Update Latency:** <30 seconds
- **Optimization Speed:** <5 seconds for portfolio
- **Curtailment Response:** <60 seconds
- **Accuracy:** 90%+ for negative price predictions
- **Revenue Improvement:** 5-15% vs no optimization

---

**Next:** [BESS Monitoring Specification](./PHASE1_BESS_MONITORING_SPECIFICATION.md)
