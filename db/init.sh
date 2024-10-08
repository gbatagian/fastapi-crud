# Create databse if not exists
psql -U "$POSTGRES_USER" -tc "SELECT 1 FROM pg_database WHERE datname = 'api'" | grep -q 1 || psql -U "$POSTGRES_USER" -c "CREATE DATABASE api"

# Create schemas
psql -U "$POSTGRES_USER" -d api -a -f opt/schema_queries/create_schema.sql

# Insert mock data
psql -U "$POSTGRES_USER" -d api -a -f opt/schema_queries/insert.sql