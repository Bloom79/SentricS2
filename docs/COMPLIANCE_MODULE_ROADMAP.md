# Compliance Module - Comprehensive Implementation Roadmap

**Last Updated**: January 2025  
**Status**: Planning & Implementation Phase

---

## 🎯 Executive Summary

This document outlines the complete compliance module implementation plan for Kronos EAM, focusing on Italian renewable energy sector requirements. The module will automate compliance management, prevent penalties, and ensure 100% deadline adherence.

---

## 📊 Current State Analysis

### ✅ Implemented
- Basic compliance records and requirements
- Workflow system with phases
- Document management foundation
- Plant-compliance association
- Basic compliance dashboard

### ❌ Missing Critical Features
1. **Recurring Obligation Engine** - No automatic annual compliance
2. **Deadline Calculator** - Manual deadline management
3. **Compliance Calendar** - No unified deadline view
4. **Phase Management** - Cannot update phase status interactively
5. **Document Requirements Tracking** - No validation per requirement
6. **Compliance Scoring** - No automated compliance percentage
7. **Penalty Calculator** - Cannot estimate costs
8. **Portal Integration Status** - No tracking of portal submissions
9. **Bulk Operations** - Cannot manage multiple plants efficiently
10. **Audit Trail** - No compliance history tracking
11. **Notifications** - No deadline alerts
12. **Compliance Reports** - No export/analytics

---

## 🚀 Implementation Plan

### **PHASE 1: Workflow Phase Management** (Priority: P0 - CRITICAL)

#### 1.1 Backend API Endpoints

**File**: `backend/app/api/v1/endpoints/workflows.py`

**New Endpoints**:
```python
# Update phase status
PUT /workflows/{workflow_id}/phases/{phase_id}/status
- Mark phase as completed/in_progress/pending
- Update completion date
- Recalculate workflow progress

# Upload documents to phase
POST /workflows/{workflow_id}/phases/{phase_id}/documents
- Upload required documents for phase
- Link documents to phase

# Add phase comments
POST /workflows/{workflow_id}/phases/{phase_id}/comments
- Add notes/comments to phase
- Track phase history

# Assign phase to user
PUT /workflows/{workflow_id}/phases/{phase_id}/assign
- Assign phase to team member
- Track assignments
```

#### 1.2 Frontend Phase Management UI

**File**: `frontend/src/pages/Workflows/WorkflowDetail.tsx`

**Features**:
- Click to mark phase as complete
- Upload documents per phase
- Add phase notes/comments
- Assign phases to users
- Real-time progress updates
- Phase dependency checking

---

### **PHASE 2: Recurring Obligation Engine** (Priority: P0 - CRITICAL)

#### 2.1 Recurring Obligation Model

**File**: `backend/app/models/recurring_obligation.py`

**Schema**:
```python
class RecurringObligation(BaseModel):
    plant_id: int
    cer_id: Optional[int]  # For CER compliance
    obligation_type: str  # 'fuel_mix', 'consumption_declaration', etc.
    entity: str  # 'GSE', 'ADM', 'DSO', 'Terna', 'Comune'
    recurrence_pattern: str  # 'annual', 'quarterly', 'monthly'
    base_deadline: dict  # {day: 31, month: 3} or {day: 16, month: 12}
    next_due_date: datetime
    last_completed_date: Optional[datetime]
    auto_create_workflow: bool
    notification_days: List[int]  # [90, 60, 30, 7]
    workflow_template_id: Optional[int]
    is_active: bool
```

#### 2.2 Recurring Obligation Service

**File**: `backend/app/services/recurring_obligation_service.py`

**Key Functions**:
- `create_recurring_obligations(plant_id)` - Auto-create from plant connection date
- `calculate_next_due_date(obligation)` - Smart date calculation with business days
- `check_upcoming_deadlines(days_ahead)` - Find obligations due soon
- `auto_create_workflows()` - Create workflows for due obligations
- `mark_completed(obligation_id, completion_date)` - Update and recalculate next due date

#### 2.3 Italian Compliance Obligations

**Default Obligations per Plant**:
1. **Fuel Mix Disclosure** (GSE) - Annual, March 31
2. **Consumption Declaration** (ADM) - Annual, March 31 (plants >20kW)
3. **License Fee Payment** (ADM) - Annual, December 16 (plants >20kW)
4. **Anti-Mafia Declaration** (GSE) - Annual, Calendar year end (if incentives >€150k)
5. **Meter Calibration** (DSO) - Every 3 years
6. **Protection System Verification** (DSO) - Every 5 years
7. **GAUDÌ Annual Reconciliation** (Terna) - Q1 each year
8. **Property Tax** (Comune) - Annual, June 16

---

### **PHASE 3: Compliance Calendar** (Priority: P1 - HIGH)

#### 3.1 Calendar Backend

**File**: `backend/app/api/v1/endpoints/compliance_calendar.py`

**Endpoints**:
```python
GET /compliance/calendar
- Get all deadlines for date range
- Filter by entity, plant, status
- Include recurring obligations

GET /compliance/calendar/upcoming
- Get deadlines in next N days
- Prioritized by urgency

GET /compliance/calendar/overdue
- Get all overdue items
- Group by plant/entity
```

#### 3.2 Calendar Frontend

**File**: `frontend/src/pages/Compliance/ComplianceCalendar.tsx`

**Features**:
- Monthly/Weekly/Daily views
- Color-coded by entity (GSE=orange, ADM=blue, etc.)
- Click to view/edit compliance record
- Drag-and-drop to reschedule
- ICal export
- Deadline filters

---

### **PHASE 4: Compliance Scoring** (Priority: P1 - HIGH)

#### 4.1 Scoring Algorithm

**File**: `backend/app/services/compliance_scoring_service.py`

**Scoring Factors**:
- **On-time Submissions** (40%) - Weighted by deadline importance
- **Document Completeness** (30%) - All required docs uploaded
- **Portal Integration Status** (20%) - Active integrations
- **No Penalties** (10%) - Zero penalty history

**Calculation**:
```python
def calculate_compliance_score(plant_id: int) -> float:
    """
    Returns score 0-100
    """
    base_score = 100
    
    # Deduct for late submissions
    late_submissions = get_late_submissions(plant_id)
    base_score -= (late_submissions * 5)  # -5 points per late submission
    
    # Deduct for missing documents
    missing_docs = get_missing_documents(plant_id)
    base_score -= (missing_docs * 3)  # -3 points per missing doc
    
    # Deduct for penalties
    penalties = get_penalties(plant_id)
    base_score -= (penalties * 10)  # -10 points per penalty
    
    return max(0, min(100, base_score))
```

#### 4.2 Score Display

- Plant-level compliance score
- Portfolio-level average
- Trend over time
- Comparison with industry average

---

### **PHASE 5: Document Requirements Tracking** (Priority: P1 - HIGH)

#### 5.1 Document Requirements Model

**Enhancement**: Add to `ComplianceRequirement.requirement_data`:
```json
{
  "required_documents": [
    {
      "type": "RID_APPLICATION_FORM",
      "name": "RID Application Form",
      "required": true,
      "entity": "GSE",
      "upload_deadline_offset_days": 0
    },
    {
      "type": "ANTI_MAFIA_DECLARATION",
      "name": "Anti-Mafia Declaration",
      "required": true,
      "entity": "GSE",
      "conditional": "incentives > 150000"
    }
  ]
}
```

#### 5.2 Document Validation

- Check required documents before marking compliance complete
- Show missing documents prominently
- Link to document upload
- Validate document types

---

### **PHASE 6: Penalty Calculator** (Priority: P2 - MEDIUM)

#### 6.1 Penalty Rules

**File**: `backend/app/core/penalty_rules.py`

**Italian Penalty Structure**:
```python
PENALTY_RULES = {
    "GSE": {
        "fuel_mix_missed": {"base": 500, "max": 2000},
        "anti_mafia_missed": {"action": "suspend_payments"},
        "rid_late_activation": {"daily_loss": "revenue_per_day"}
    },
    "ADM": {
        "consumption_declaration_missed": {"base": 1000, "max": 5000},
        "license_fee_missed": {"action": "suspend_license"},
        "unlicensed_operation": {"base": 5000, "max": 15000}
    },
    "DSO": {
        "meter_calibration_expired": {"action": "disconnect"},
        "protection_check_expired": {"base": 500, "max": 2000}
    }
}
```

#### 6.2 Calculator UI

- Estimate penalty before deadline
- Show cost of missed deadlines
- ROI calculator for compliance tools

---

### **PHASE 7: Portal Integration Status** (Priority: P2 - MEDIUM)

#### 7.1 Integration Status Tracking

**Model Enhancement**: Add to `Plant` or `ComplianceRecord`:
```python
portal_integration_status = Column(JSON, default=dict)
# {
#   "GSE": {"status": "connected", "last_sync": "2025-01-15", "mfa_enabled": true},
#   "Terna": {"status": "connected", "last_sync": "2025-01-10"},
#   "ADM": {"status": "manual", "last_sync": null}
# }
```

#### 7.2 Status Dashboard

- Show portal connection status
- Last sync time
- MFA status (required for GSE from 05/03/2025)
- Integration health indicators

---

### **PHASE 8: Bulk Operations** (Priority: P2 - MEDIUM)

#### 8.1 Bulk Compliance Actions

**Endpoints**:
```python
POST /compliance/bulk/create-workflows
- Create workflows for multiple plants
- Apply same template to portfolio

POST /compliance/bulk/update-status
- Update multiple compliance records
- Bulk document upload

POST /compliance/bulk/export
- Export compliance data for multiple plants
- Generate compliance reports
```

#### 8.2 UI Features

- Multi-select plants
- Bulk workflow creation
- Portfolio compliance view
- Batch document upload

---

### **PHASE 9: Audit Trail** (Priority: P2 - MEDIUM)

#### 9.1 Compliance History

**Model**: `ComplianceAuditLog`
```python
class ComplianceAuditLog(BaseModel):
    compliance_record_id: int
    action: str  # 'created', 'updated', 'completed', 'document_uploaded'
    user_id: int
    timestamp: datetime
    changes: dict  # Before/after values
    notes: str
```

#### 9.2 Audit UI

- Show compliance history per record
- Track all changes
- Export audit reports
- Compliance proof for auditors

---

### **PHASE 10: Notifications & Alerts** (Priority: P1 - HIGH)

#### 10.1 Notification Service

**File**: `backend/app/services/compliance_notification_service.py`

**Notification Types**:
- Deadline approaching (90, 60, 30, 7 days)
- Deadline overdue
- Document missing
- Portal sync failed
- Compliance score dropped

#### 10.2 Notification Channels

- In-app notifications
- Email alerts
- SMS (for critical deadlines)
- Slack/Teams integration

---

### **PHASE 11: Compliance Reports** (Priority: P2 - MEDIUM)

#### 11.1 Report Types

1. **Plant Compliance Report** - Single plant status
2. **Portfolio Compliance Report** - All plants overview
3. **Entity Compliance Report** - By entity (GSE, ADM, etc.)
4. **Deadline Calendar Report** - Upcoming deadlines
5. **Penalty Risk Report** - Potential penalties
6. **Compliance Score Report** - Score trends

#### 11.2 Export Formats

- PDF (formatted reports)
- Excel (data export)
- CSV (bulk data)
- ICal (deadline calendar)

---

## 📋 Implementation Priority

### **Sprint 1 (Weeks 1-2)** - Critical Path
1. ✅ Workflow phase management (status updates, completion)
2. ✅ Recurring obligation engine
3. ✅ Compliance calendar basic view

### **Sprint 2 (Weeks 3-4)** - High Value
4. ✅ Compliance scoring
5. ✅ Document requirements tracking
6. ✅ Notifications & alerts

### **Sprint 3 (Weeks 5-6)** - Optimization
7. ✅ Penalty calculator
8. ✅ Portal integration status
9. ✅ Bulk operations

### **Sprint 4 (Weeks 7-8)** - Advanced Features
10. ✅ Audit trail
11. ✅ Compliance reports
12. ✅ Advanced calendar features

---

## 🔗 Integration Points

### **With Existing Modules**:
- **Plants**: Compliance tied to plant lifecycle
- **Documents**: Required documents linked to compliance
- **Workflows**: Compliance generates workflows
- **CER**: CER-specific compliance obligations
- **Integrations**: Portal status tracking

### **External Integrations**:
- **GSE Portal**: Document submission tracking
- **Terna GAUDÌ**: Registration status
- **ADM Portal**: License and declaration status
- **DSO APIs**: Connection and meter status

---

## 📊 Success Metrics

- **Zero Missed Deadlines**: 100% on-time compliance
- **Compliance Score**: Average >95%
- **Penalty Reduction**: 90% reduction in penalties
- **Time Savings**: 80% reduction in manual compliance work
- **User Satisfaction**: >4.5/5 rating

---

## 🎯 Next Steps

1. Implement workflow phase management APIs
2. Create recurring obligation engine
3. Build compliance calendar
4. Add compliance scoring
5. Implement notifications

---

*This roadmap is a living document and will be updated as features are implemented.*

