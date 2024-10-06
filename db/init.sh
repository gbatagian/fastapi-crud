# Create databse if not exists
psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'api'" | grep -q 1 || psql -U postgres -c "CREATE DATABASE api"

# Create schemas
psql -U postgres -d api -a -f opt/schema_queries/create_schema.sql

# Insert mock data
psql -U postgres -d api -a -f opt/schema_queries/insert.sql