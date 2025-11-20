"""
Password validation utilities
Enforces strong password policies to prevent weak passwords
"""

import re
from typing import List, Tuple
from app.core.config import settings


def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Validate password against configured security policies.

    Args:
        password: The password to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check minimum length
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long")

    # Check for uppercase letters
    if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")

    # Check for lowercase letters
    if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")

    # Check for digits
    if settings.PASSWORD_REQUIRE_DIGITS and not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")

    # Check for special characters
    if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;`~]', password):
        errors.append("Password must contain at least one special character")

    # Check for common weak patterns
    common_weak_passwords = [
        'password', '12345678', 'qwerty', 'abc123', 'letmein',
        'admin', 'welcome', 'monkey', 'dragon', 'master'
    ]
    if password.lower() in common_weak_passwords:
        errors.append("Password is too common and easily guessable")

    # Check for repeated characters (e.g., "aaaa", "1111")
    if re.search(r'(.)\1{3,}', password):
        errors.append("Password contains too many repeated characters")

    # Check for sequential characters (e.g., "1234", "abcd")
    sequential_patterns = ['0123', '1234', '2345', '3456', '4567', '5678', '6789',
                          'abcd', 'bcde', 'cdef', 'defg', 'efgh', 'fghi', 'ghij']
    password_lower = password.lower()
    for pattern in sequential_patterns:
        if pattern in password_lower:
            errors.append("Password contains sequential characters")
            break

    is_valid = len(errors) == 0
    return is_valid, errors


def get_password_requirements() -> dict:
    """
    Get current password requirements for display to users.

    Returns:
        Dictionary of password requirements
    """
    return {
        "min_length": settings.PASSWORD_MIN_LENGTH,
        "require_uppercase": settings.PASSWORD_REQUIRE_UPPERCASE,
        "require_lowercase": settings.PASSWORD_REQUIRE_LOWERCASE,
        "require_digits": settings.PASSWORD_REQUIRE_DIGITS,
        "require_special": settings.PASSWORD_REQUIRE_SPECIAL,
        "description": _get_requirements_text()
    }


def _get_requirements_text() -> str:
    """Generate human-readable password requirements text"""
    requirements = [f"at least {settings.PASSWORD_MIN_LENGTH} characters"]

    if settings.PASSWORD_REQUIRE_UPPERCASE:
        requirements.append("one uppercase letter")

    if settings.PASSWORD_REQUIRE_LOWERCASE:
        requirements.append("one lowercase letter")

    if settings.PASSWORD_REQUIRE_DIGITS:
        requirements.append("one digit")

    if settings.PASSWORD_REQUIRE_SPECIAL:
        requirements.append("one special character (!@#$%^&*...)")

    return "Password must contain: " + ", ".join(requirements)
