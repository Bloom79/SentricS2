# Database Dump and Import Scripts

Scripts for dumping and importing database schema and seed data, with special handling for user authentication data.

## Overview

These scripts allow you to:
- **Dump database schema** (structure only, no data)
- **Dump seed data** (excluding sensitive authentication information)
- **Create safe user seeds** (users with placeholder passwords)
- **Import dumps** into new databases

## Scripts

### 1. `dump_schema.py` - Schema Dump

Dumps the complete database structure (tables, indexes, foreign keys) without any data.

```bash
cd backend
python scripts/dump_schema.py
```

**Output**: `schema_dump_YYYYMMDD_HHMMSS.sql`

**What it includes**:
- All table definitions
- Indexes
- Foreign key constraints
- PostGIS extensions
- Column types and constraints

**What it excludes**:
- All data
- Alembic version table structure (handled by migrations)

### 2. `dump_seed_data.py` - Seed Data Dump

Dumps all seed data from the database, excluding sensitive authentication information.

```bash
cd backend
python scripts/dump_seed_data.py
```

**Output**: 
- `seed_data_dump_YYYYMMDD_HHMMSS.sql` - All seed data
- `safe_user_seed_YYYYMMDD_HHMMSS.sql` - Users with placeholder passwords

**What it includes**:
- All tables with data (except excluded tables)
- Proper dependency ordering
- Soft-deleted records are excluded

**What it excludes**:
- `password_hash` from users table
- `mfa_secret` from users table
- `failed_login_attempts` from users table
- `locked_until` from users table
- Alembic version table

**Security Notes**:
- User passwords are **NEVER** dumped
- Users are created with placeholder password hash (`CHANGE_ME`)
- **MUST** update passwords after import

### 3. `dump_all.py` - Complete Dump

Runs both schema and seed data dumps in sequence.

```bash
cd backend
python scripts/dump_all.py
```

**Output**: Creates all three dump files:
1. Schema dump
2. Seed data dump
3. Safe user seed

### 4. `import_dumps.py` - Import Dumps

Imports schema and seed data dumps into a database.

```bash
cd backend

# Import specific files
python scripts/import_dumps.py \
    --schema schema_dump_20250101_120000.sql \
    --seed seed_data_dump_20250101_120000.sql \
    --users safe_user_seed_20250101_120000.sql

# Auto-detect files in a directory
python scripts/import_dumps.py --all ./dumps/
```

**Import Order**:
1. Schema (if provided)
2. Seed data (if provided)
3. Users (if provided, with confirmation prompt)

## Usage Examples

### Dump Everything

```bash
cd backend
python scripts/dump_all.py
```

This creates:
- `schema_dump_20250101_120000.sql`
- `seed_data_dump_20250101_120000.sql`
- `safe_user_seed_20250101_120000.sql`

### Import into New Database

```bash
# 1. Create database
createdb kronos_eam_new

# 2. Update DATABASE_URL in .env
export DATABASE_URL="postgresql://user:pass@localhost/kronos_eam_new"

# 3. Import schema
python scripts/import_dumps.py --schema schema_dump_20250101_120000.sql

# 4. Import seed data
python scripts/import_dumps.py --seed seed_data_dump_20250101_120000.sql

# 5. Import users (with confirmation)
python scripts/import_dumps.py --users safe_user_seed_20250101_120000.sql

# 6. Update user passwords
python <<EOF
from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash

db = next(get_db())
user = db.query(User).filter(User.email == "test@example.com").first()
if user:
    user.password_hash = get_password_hash("new_password")
    db.commit()
    print("Password updated")
EOF
```

### Import All at Once

```bash
# Put all dump files in a directory
mkdir -p dumps/
cp schema_dump_*.sql dumps/
cp seed_data_dump_*.sql dumps/
cp safe_user_seed_*.sql dumps/

# Import all
python scripts/import_dumps.py --all ./dumps/
```

## Security Considerations

### ⚠️ Important Security Notes

1. **Password Hashes**: Never dumped or included in exports
2. **MFA Secrets**: Never dumped
3. **User Seeds**: Use placeholder passwords that MUST be changed
4. **Review Before Import**: Always review dump files before importing
5. **Production**: Never import user seeds directly to production

### Safe User Seed Format

Users in the safe seed file have:
- All user data (name, email, role, etc.)
- Placeholder password hash (must be changed)
- No MFA secrets
- No security-sensitive fields

After import, update passwords:

```python
from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash

db = next(get_db())
for user in db.query(User).all():
    # Set new password
    user.password_hash = get_password_hash("secure_password_here")
db.commit()
```

## File Structure

```
backend/scripts/
├── dump_schema.py      # Schema dump only
├── dump_seed_data.py   # Seed data dump
├── dump_all.py         # Combined dump
├── import_dumps.py     # Import script
└── README_DUMPS.md     # This file
```

## Troubleshooting

### Schema Import Fails

- Make sure PostGIS extension is available: `CREATE EXTENSION IF NOT EXISTS postgis;`
- Check database user has CREATE privileges
- Run migrations first: `alembic upgrade head`

### Seed Data Import Fails

- Check foreign key dependencies are satisfied
- Verify tenant data exists before importing dependent data
- Check for constraint violations

### User Import Issues

- Review the safe user seed file
- Make sure tenant IDs match existing tenants
- Update passwords immediately after import

## Best Practices

1. **Always dump schema first**, then seed data
2. **Review dump files** before importing
3. **Test imports** in a development environment first
4. **Update passwords** immediately after user import
5. **Keep dumps secure** - they may contain sensitive business data
6. **Version control** schema dumps, but NOT seed data with real user info

## Integration with Alembic

These dumps work alongside Alembic migrations:

- **Schema dumps**: Capture current structure (for reference)
- **Alembic migrations**: Track schema changes over time
- **Seed data**: Initial data for development/testing

Use Alembic for schema evolution, use dumps for:
- Backup/restore
- Setting up new environments
- Sharing reference data

---

**Last Updated**: January 2025

