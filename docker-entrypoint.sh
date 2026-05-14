#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "PostgreSQL is ready!"

echo "Initializing database..."
python -c "import database; database.init_db()"

echo "Running indexer..."
python generate_test_data.py sample_data 30 && python indexer.py sample_data

echo "?? Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000