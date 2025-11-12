# PostgreSQL Local Development Setup

## Step 1: Start PostgreSQL Container (WITHOUT Superuser)

**IMPORTANT**: We create the `ayni_user` role WITHOUT superuser privileges to enforce Row-Level Security (RLS) policies. Superuser roles bypass RLS even with `FORCE ROW LEVEL SECURITY` enabled.

```bash
docker run --name ayni-postgres \
  -e POSTGRES_USER=ayni_user \
  -e POSTGRES_PASSWORD=928236543 \
  -e POSTGRES_DB=ayni_dev \
  -p 5432:5432 \
  -d postgres:15
```

## Step 2: Remove Superuser Privileges (Required for RLS)

After the container starts, the `ayni_user` role is created as a SUPERUSER by default. We need to remove these privileges:

```bash
# Connect to the database and remove superuser privileges
docker exec -it ayni-postgres psql -U ayni_user -d ayni_dev -c "ALTER ROLE ayni_user NOSUPERUSER NOBYPASSRLS;"

# Verify the role no longer has superuser privileges
docker exec -it ayni-postgres psql -U ayni_user -d ayni_dev -c "SELECT rolname, rolsuper, rolbypassrls FROM pg_roles WHERE rolname = 'ayni_user';"
```

Expected output:
```
  rolname   | rolsuper | rolbypassrls
------------+----------+--------------
 ayni_user  | f        | f
```

## Step 3: Run Database Migrations

```bash
cd backend
uv run alembic upgrade head
```

## Managing the Database Container

### Stop the database:
```bash
docker stop ayni-postgres
```

### Start it again:
```bash
docker start ayni-postgres
```

### View logs:
```bash
docker logs ayni-postgres
```

### Connect to database with psql:
```bash
docker exec -it ayni-postgres psql -U ayni_user -d ayni_dev
```

### Remove container completely:
```bash
docker stop ayni-postgres
docker rm ayni-postgres
```

## Adding Superuser Privileges (If Needed for Admin Tasks)

**WARNING**: Only add superuser privileges temporarily for specific admin tasks. Remember to remove them afterwards to maintain RLS enforcement.

```bash
# Add superuser privileges temporarily
docker exec -it ayni-postgres psql -U postgres -d ayni_dev -c "ALTER ROLE ayni_user SUPERUSER BYPASSRLS;"

# ... perform admin tasks ...

# IMPORTANT: Remove superuser privileges after admin tasks
docker exec -it ayni-postgres psql -U postgres -d ayni_dev -c "ALTER ROLE ayni_user NOSUPERUSER NOBYPASSRLS;"
```

**Note**: When using superuser privileges, you must connect as the `postgres` user since `ayni_user` won't have permission to modify its own role.

## Troubleshooting

### If RLS tests are failing with "seeing all users":
This means the `ayni_user` role still has SUPERUSER or BYPASSRLS privileges. Run:
```bash
docker exec -it ayni-postgres psql -U postgres -d ayni_dev -c "ALTER ROLE ayni_user NOSUPERUSER NOBYPASSRLS;"
```

### If you need to reset the database completely:
```bash
docker stop ayni-postgres
docker rm ayni-postgres
# Then run Step 1 and Step 2 again
```

## Alternative: Create Database with Correct Permissions from Start

If you want to avoid Step 2, you can create a custom initialization script:

```bash
# Create init script directory
mkdir -p postgres-init

# Create initialization script
cat > postgres-init/01-setup-user.sql << 'EOF'
-- This runs after the default user is created
ALTER ROLE ayni_user NOSUPERUSER NOBYPASSRLS;
EOF

# Run container with init script
docker run --name ayni-postgres \
  -e POSTGRES_USER=ayni_user \
  -e POSTGRES_PASSWORD=928236543 \
  -e POSTGRES_DB=ayni_dev \
  -p 5432:5432 \
  -v $(pwd)/postgres-init:/docker-entrypoint-initdb.d \
  -d postgres:15
```
