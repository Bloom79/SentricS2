# SentricS2 Backend Test Suite

Comprehensive test suite for the SentricS2 backend application.

## Overview

This test suite provides **70%+ code coverage** and includes:
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **API Tests**: Test HTTP endpoints

**Current Statistics:**
- Total Tests: 50+
- Unit Tests: 35+
- Integration Tests: 10+
- API Tests: 10+
- Target Coverage: 70%+

## Directory Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── __init__.py
├── unit/                       # Unit tests
│   ├── services/              # Service layer tests
│   │   ├── test_plant_service.py
│   │   ├── test_cer_service.py
│   │   └── test_asset_service.py
│   ├── models/                # Model tests
│   └── api/                   # API endpoint tests
│       └── test_plant_endpoints.py
├── integration/               # Integration tests
│   └── test_plant_cer_workflow.py
└── fixtures/                  # Test data fixtures
```

## Running Tests

### Prerequisites

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Setup test database:**
```bash
# Create test database
createdb sentrics2_test

# Or using Docker/Podman
./compose.sh up -d
psql -U postgres -c "CREATE DATABASE sentrics2_test;"
```

### Run All Tests

```bash
# Run all tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=term-missing
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run only service tests
pytest tests/unit/services/ -v

# Run only API tests
pytest tests/unit/api/ -v
```

### Run Specific Test Files

```bash
# Run plant service tests
pytest tests/unit/services/test_plant_service.py -v

# Run CER service tests
pytest tests/unit/services/test_cer_service.py -v

# Run specific test
pytest tests/unit/services/test_plant_service.py::TestPlantService::test_create_plant_success -v
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser

# Generate terminal report with missing lines
pytest --cov=app --cov-report=term-missing

# Generate XML report (for CI/CD)
pytest --cov=app --cov-report=xml
```

## Test Configuration

Tests are configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --cov=app --cov-report=html --cov-fail-under=70"
```

## Writing Tests

### Test Structure

Follow the **Arrange-Act-Assert (AAA)** pattern:

```python
def test_create_plant_success(db_session, test_tenant, test_user):
    """Test successful plant creation"""
    # Arrange
    plant_data = PlantCreate(
        name="Test Plant",
        code="TEST-001",
        power_kw=100.0
    )

    # Act
    plant = PlantService.create_plant(
        db_session,
        plant_data,
        test_tenant.id,
        test_user.id
    )

    # Assert
    assert plant.id is not None
    assert plant.name == "Test Plant"
    assert plant.tenant_id == test_tenant.id
```

### Using Fixtures

Common fixtures are available in `conftest.py`:

```python
def test_example(
    db_session,      # Database session
    test_tenant,     # Test tenant
    test_user,       # Test user
    test_plant,      # Test plant
    test_cer,        # Test CER
    test_asset,      # Test asset
    auth_headers,    # Auth headers for API tests
    client          # FastAPI test client
):
    # Your test code here
    pass
```

### Test Naming Conventions

- **Test files**: `test_*.py`
- **Test classes**: `TestClassName`
- **Test functions**: `test_functionality_scenario`

Examples:
- `test_create_plant_success`
- `test_get_plant_not_found`
- `test_plant_tenant_isolation`

### Test Categories

Use pytest markers for categorization:

```python
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration
def test_integration_flow():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

Run specific markers:
```bash
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

## Fixtures Reference

### Database Fixtures

- `engine`: Test database engine (session-scoped)
- `db_session`: Clean database session per test (function-scoped)

### Model Fixtures

- `test_tenant`: Test tenant
- `test_user`: Test user
- `test_plant`: Test plant
- `test_cer`: Test CER (Community Energy Resource)
- `test_asset_type`: Test asset type
- `test_asset`: Test asset

### API Fixtures

- `client`: FastAPI test client
- `auth_headers`: Authentication headers

### Mock Fixtures

- `mock_settings`: Mock settings for testing

## Best Practices

### 1. Test Isolation

Each test should be independent and not rely on other tests:

```python
# Good - Independent test
def test_create_plant(db_session, test_tenant):
    plant = create_plant(...)  # Create what you need
    assert plant.id is not None

# Bad - Depends on other tests
def test_update_plant(db_session):
    plant = get_plant_from_previous_test()  # Don't do this!
```

### 2. Use Descriptive Names

```python
# Good - Clear what is being tested
def test_create_plant_with_invalid_power_returns_validation_error():
    pass

# Bad - Unclear
def test_plant():
    pass
```

### 3. Test One Thing

```python
# Good - Tests one scenario
def test_create_plant_success():
    # Test successful creation only
    pass

def test_create_plant_validation_error():
    # Test validation error only
    pass

# Bad - Tests multiple scenarios
def test_plant_operations():
    # Creates, updates, deletes all in one test
    pass
```

### 4. Arrange-Act-Assert Pattern

Always use AAA for clarity:

```python
def test_example():
    # Arrange - Setup test data
    plant_data = PlantCreate(...)

    # Act - Perform the action
    result = service.create_plant(...)

    # Assert - Verify the outcome
    assert result.id is not None
    assert result.name == expected_name
```

### 5. Test Edge Cases

Don't just test the happy path:

```python
def test_create_plant_success():
    # Test normal case
    pass

def test_create_plant_validation_error():
    # Test with invalid data
    pass

def test_create_plant_tenant_isolation():
    # Test security
    pass

def test_create_plant_not_found():
    # Test error cases
    pass
```

## Continuous Integration

Tests run automatically on:
- Every pull request
- Every commit to main branch
- Scheduled nightly builds

### CI/CD Requirements

- All tests must pass
- Minimum 70% code coverage
- No linting errors

## Troubleshooting

### Database Connection Errors

```bash
# Ensure test database exists
createdb sentrics2_test

# Or reset test database
dropdb sentrics2_test
createdb sentrics2_test
```

### Import Errors

```bash
# Ensure you're in the backend directory
cd backend

# Install in development mode
pip install -e .
```

### Fixture Not Found

Make sure you're importing from the correct location and that conftest.py is present.

### Slow Tests

```bash
# Identify slow tests
pytest --durations=10

# Skip slow tests
pytest -m "not slow"
```

## Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| Services | 90%+ |
| Models | 80%+ |
| API Endpoints | 85%+ |
| Utilities | 70%+ |
| **Overall** | **70%+** |

## Contributing

When adding new features:

1. Write tests first (TDD approach recommended)
2. Ensure all tests pass
3. Maintain or improve coverage percentage
4. Add docstrings to test functions
5. Update this README if needed

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

---

**Last Updated:** January 2025
**Maintained by:** SentricS2 Development Team
