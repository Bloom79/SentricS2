# Seed Data Scripts

## CER Seed Data (`seed_cer_data.py`)

Comprehensive seed data script that creates all CER-related test data.

### What it creates:

1. **3 CERs (Renewable Energy Communities)**
   - Solar Community Milan (Active, Cooperative)
   - Wind Energy Cooperative Turin (Active, Cooperative)
   - Mixed Energy Community Rome (Pending, Association)

2. **5 Plants** (linked to CERs)
   - Solar Farm Milan North (150kW) → CER 1
   - Solar Array Milan Center (100kW) → CER 1
   - Wind Farm Turin Hills (180kW) → CER 2
   - Solar Park Rome East (200kW) → CER 3
   - Biomass Plant Rome (120kW) → CER 3

3. **6 CER Members**
   - Giuseppe Rossi (Prosumer) → CER 1
   - Maria Bianchi (Producer) → CER 1
   - Tech Startup Milano SRL (Consumer) → CER 1
   - Antonio Verdi (Prosumer) → CER 2
   - Residential Building Turin (Consumer) → CER 2
   - Francesca Neri (Producer) → CER 3

4. **6 Member Assets**
   - Solar panels and battery storage systems for prosumers/producers

5. **4 Participation Requests**
   - Mix of pending, approved, and rejected requests

6. **6 Compliance Requirements**
   - 3 CER-specific requirements (GSE, ARERA)
   - 3 Plant-specific requirements

7. **6 Compliance Records**
   - Linked to requirements with various statuses and due dates

8. **6 Documents**
   - Certificates, permits, reports
   - Linked to CERs and Plants
   - Some expiring soon for testing

### Usage:

```bash
cd kronos-eam-consolidated/backend
python scripts/seed_cer_data.py
```

### Prerequisites:

- Database must be initialized
- Demo tenant and test user must exist (created by `seed_test_data.py` or startup script)
- All migrations must be applied

### Notes:

- Script is idempotent - it checks for existing data before creating
- Uses tenant_id="demo" and user_id=1 by default
- All dates are relative to current time for realistic testing

