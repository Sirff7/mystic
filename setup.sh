#!/bin/bash
createdb mystic 2>/dev/null || echo "Database already exists - skipping"
psql -d mystic -f schema.sql
uv sync