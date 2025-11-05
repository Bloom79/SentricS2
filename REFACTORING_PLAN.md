# Code Refactoring Plan - Week 12-15

**Date:** January 2025
**Status:** 🚧 In Progress

---

## 📋 Analysis Summary

### Large Files Requiring Splitting (>500 lines)

| File | Lines | Priority | Action |
|------|-------|----------|--------|
| `api/v1/endpoints/cer.py` | 1,146 | 🔴 HIGH | Split into modules |
| `api/v1/endpoints/dev.py` | 850 | 🟡 MEDIUM | Keep as is (test data) |
| `services/italian_workflow_templates.py` | 653 | 🟢 LOW | Keep as is (data file) |
| `services/cer_service.py` | 651 | 🔴 HIGH | Refactor + extract helpers |
| `services/billing_service.py` | 616 | 🟡 MEDIUM | Refactor complex functions |
| `api/v1/sites.py` | 598 | 🟡 MEDIUM | Refactor |
| `api/v1/endpoints/workflows.py` | 540 | 🟡 MEDIUM | Refactor |

### Complex Functions (C901 - 19 total)

**Most Complex (Complexity > 20):**
1. ❌ `seed_test_data()` - 45 (dev.py) - Keep as is
2. `import_panels_from_csv()` - 23 (bulk_import_service.py) - Refactor
3. `get_cer_compliance_records()` - 21 (cer.py) - Refactor
4. `list_records()` - 20 (compliance.py) - Refactor

**High Complexity (15-19):**
5. `update_phase_status()` - 17 (workflow_phases.py) - Refactor
6. `validate_panel_row()` - 16 (bulk_import_service.py) - Refactor
7. `calculate_shared_energy()` - 16 (energy_service.py) - Refactor
8. `update_member()` - 16 (cer_service.py) - Refactor
9. `get_cer_compliance_requirements()` - 15 (cer.py) - Refactor

**Medium Complexity (11-14):**
10. `get_cer_compliance()` - 14 (cer.py)
11. `list_workflows()` - 14 (workflow_service.py)
12. `get_workflow()` - 14 (workflows.py)
13. `create_document()` - 13 (documents.py)
14. `create_billing_transaction()` - 13 (billing_service.py)
15. `update_document()` - 12 (documents.py)
16. `assign_panels_to_string()` - 12 (string_config_service.py)
17. `list_workflows()` - 11 (workflows.py)
18. `add_member()` - 11 (cer_service.py)
19. `create_record()` - 11 (compliance.py)

### Unused Imports (F401 - 78 total)

**Distribution by file type:**
- Models: ~20 unused imports
- Services: ~25 unused imports
- API endpoints: ~20 unused imports
- Schemas: ~10 unused imports
- Core modules: ~3 unused imports

---

## 🎯 Refactoring Strategy

### Phase 1: Foundation (Week 12)
✅ Clean up all 78 unused imports
✅ Create base service class with common patterns
✅ Update existing services to inherit from base

### Phase 2: Service Refactoring (Week 13)
- Extract helper functions from complex service methods
- Apply DRY principles
- Reduce cyclomatic complexity to < 10

### Phase 3: Endpoint Refactoring (Week 14)
- Refactor complex endpoint handlers
- Move business logic to services
- Simplify error handling

### Phase 4: File Splitting (Week 15)
- Split cer.py (1146 lines) into logical modules
- Consider splitting cer_service.py
- Organize into sub-packages if needed

---

## 📝 Detailed Plan

### Task 1: Clean Up Unused Imports (78 total)

**Approach:** Remove unused imports file by file

**Priority Files:**
1. `services/billing_service.py` - 7 unused
2. `models/` - ~20 unused (Boolean, DateTime, etc.)
3. `core/` modules - Geography functions, config imports
4. `api/v1/endpoints/` - Various unused

**Method:** Manual review with verification

---

### Task 2: Create Base Service Class

**Location:** `backend/app/services/base.py`

**Features:**
```python
class BaseService:
    """Base class for all service classes with common patterns"""

    @staticmethod
    def _apply_tenant_filter(query, model, tenant_id: str):
        """Apply tenant isolation filter"""
        pass

    @staticmethod
    def _apply_deleted_filter(query, model):
        """Apply soft delete filter"""
        pass

    @staticmethod
    def _get_by_id(db, model, id, tenant_id):
        """Standard get by ID with tenant isolation"""
        pass

    @staticmethod
    def _paginate(query, skip: int, limit: int):
        """Standard pagination"""
        pass
```

**Benefits:**
- Reduces code duplication
- Standardizes patterns across services
- Easier testing and maintenance

---

### Task 3: Refactor Complex Functions

#### Priority 1: `get_cer_compliance_records()` - Complexity 21

**File:** `api/v1/endpoints/cer.py:660`

**Refactoring approach:**
- Extract filtering logic into separate functions
- Extract response building into helper
- Move business logic to service layer

**Target complexity:** < 10

---

#### Priority 2: `import_panels_from_csv()` - Complexity 23

**File:** `services/bulk_import_service.py:141`

**Refactoring approach:**
- Extract CSV parsing into separate method
- Extract validation into separate method (already complex at 16)
- Extract database insertion into separate method
- Create `PanelImporter` helper class

**Target complexity:** < 10 per method

---

#### Priority 3: `list_records()` - Complexity 20

**File:** `api/v1/endpoints/compliance.py:95`

**Refactoring approach:**
- Extract query building logic
- Move to service layer
- Simplify filtering logic

**Target complexity:** < 10

---

### Task 4: Split Large Files

#### Priority: `api/v1/endpoints/cer.py` (1,146 lines)

**Proposed structure:**
```
api/v1/endpoints/cer/
├── __init__.py (router aggregation)
├── communities.py (CER CRUD)
├── members.py (Member management)
├── compliance.py (Compliance endpoints)
├── documents.py (Document stats)
├── plants.py (Plant linking)
└── assets.py (Member assets)
```

**Benefits:**
- Easier navigation
- Better code organization
- Reduced merge conflicts
- Clearer responsibility separation

---

## 🎯 Success Metrics

### Quantitative
- [x] Unused imports: 78 → 0
- [ ] Complex functions: 19 → < 10
- [ ] Average function complexity: Reduce by 30%
- [ ] Files > 500 lines: 7 → < 5
- [ ] Service inheritance: 0% → 80%+

### Qualitative
- [ ] Improved code readability
- [ ] Better separation of concerns
- [ ] Easier testing
- [ ] Reduced technical debt

---

## ⚠️ Risk Mitigation

1. **Testing:** Run full test suite after each major change
2. **Incremental:** One file/function at a time
3. **Version Control:** Commit frequently with clear messages
4. **Backward Compatibility:** Maintain all existing APIs
5. **Code Review:** Self-review before committing

---

## 📅 Timeline

- **Week 12 (Days 1-2):** Clean imports, create base service
- **Week 13 (Days 3-5):** Refactor service layer (8 functions)
- **Week 14 (Days 6-8):** Refactor endpoints (11 functions)
- **Week 15 (Days 9-10):** Split large files, final testing

**Total Estimated Time:** 10 days

---

**Status:** Planning complete, ready to execute

**Next Step:** Begin Phase 1 - Clean up unused imports
