# Create databse if not exists
psql -U "$POSTGRES_USER" -tc "SELECT 1 FROM pg_database WHERE datname = 'api'" | grep -q 1 || psql -U "$POSTGRES_USER" -c "CREATE DATABASE api"

# Set max_connections
psql -U "$POSTGRES_USER" -c "ALTER SYSTEM SET max_connections = '$POSTGRES_MAX_CONNECTIONS';"
psql -U "$POSTGRES_USER" -c "SELECT pg_reload_conf();"

# Create schemas
psql -U "$POSTGRES_USER" -d api -a -f opt/schema_queries/create_schema.sql

# Insert mock data
psql -U "$POSTGRES_USER" -d api -a -f opt/schema_queries/insert.sql