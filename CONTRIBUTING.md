# Contributing to SentricS2

First off, thank you for considering contributing to SentricS2! It's people like you that make SentricS2 such a great tool for the renewable energy sector.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples**
* **Describe the behavior you observed and what you expected**
* **Include screenshots if relevant**
* **Include your environment details** (OS, Python version, Node version, etc.)

###suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Explain why this enhancement would be useful**
* **List any alternatives you've considered**

### Pull Requests

* Fill in the required template
* Follow the style guides
* Include appropriate test cases
* Update documentation as needed
* Ensure all tests pass

## Development Setup

1. **Fork and clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/SentricS2.git
cd SentricS2
```

2. **Set up backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

3. **Set up frontend**
```bash
cd frontend
npm install
```

4. **Create a branch**
```bash
git checkout -b feature/your-feature-name
```

## Style Guides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Example:
```
Add rate limiting to API endpoints

- Implement SlowAPI for rate limiting
- Configure limits per endpoint
- Add Redis backend for distributed rate limiting
- Update documentation

Fixes #123
```

### Python Style Guide

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Use [Black](https://black.readthedocs.io/) for code formatting
* Use type hints for all functions
* Maximum line length: 100 characters
* Write docstrings for all public functions

```python
def calculate_cer_capacity(
    db: Session,
    cer_id: int,
    tenant_id: str
) -> float:
    """
    Calculate total capacity for a CER.

    Args:
        db: Database session
        cer_id: CER identifier
        tenant_id: Tenant identifier

    Returns:
        Total capacity in kW

    Raises:
        NotFoundException: If CER not found
    """
    ...
```

### TypeScript/React Style Guide

* Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
* Use functional components with hooks
* Use TypeScript for all new code
* Prefer named exports over default exports
* Use meaningful variable names

```typescript
interface PlantCardProps {
  plant: Plant;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
}

export const PlantCard: React.FC<PlantCardProps> = ({
  plant,
  onEdit,
  onDelete,
}) => {
  // Component implementation
};
```

### Testing Guidelines

* Write tests for all new features
* Maintain minimum 70% code coverage
* Use descriptive test names
* Follow AAA pattern (Arrange, Act, Assert)

**Backend tests:**
```python
def test_create_plant_success(db_session, test_tenant):
    """Test successful plant creation"""
    # Arrange
    plant_data = PlantCreate(
        name="Test Plant",
        code="TEST001",
        power_kw=100.0,
        ...
    )

    # Act
    plant = plant_service.create_plant(
        db_session,
        plant_data,
        test_tenant.id,
        1
    )

    # Assert
    assert plant.id is not None
    assert plant.name == "Test Plant"
    assert plant.tenant_id == test_tenant.id
```

**Frontend tests:**
```typescript
describe('PlantCard', () => {
  it('renders plant information correctly', () => {
    const plant = createMockPlant();
    render(<PlantCard plant={plant} />);

    expect(screen.getByText(plant.name)).toBeInTheDocument();
    expect(screen.getByText(plant.code)).toBeInTheDocument();
  });
});
```

## Code Review Process

1. All submissions require review
2. Reviewers will check:
   - Code quality and style
   - Test coverage
   - Documentation updates
   - Security implications
   - Performance impact
3. Address feedback promptly
4. Once approved, maintainers will merge

## Project Structure

```
SentricS2/
├── backend/          # Python/FastAPI backend
│   ├── app/
│   │   ├── api/     # API endpoints
│   │   ├── models/  # Database models
│   │   ├── schemas/ # Pydantic schemas
│   │   └── services/# Business logic
│   └── tests/       # Backend tests
└── frontend/        # React/TypeScript frontend
    ├── src/
    │   ├── pages/   # Page components
    │   ├── components/# Reusable components
    │   └── services/# API clients
    └── tests/       # Frontend tests
```

## Running Tests

```bash
# Backend tests
cd backend
pytest --cov=app tests/

# Frontend tests
cd frontend
npm test

# Linting
cd backend
flake8 app
black --check app
mypy app

cd frontend
npm run lint
```

## Documentation

* Update README.md if you change functionality
* Add JSDoc/docstrings for new functions
* Update API documentation if you change endpoints
* Add examples for new features

## Questions?

Feel free to:
* Open an issue for questions
* Start a discussion in GitHub Discussions
* Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to SentricS2! 🎉
