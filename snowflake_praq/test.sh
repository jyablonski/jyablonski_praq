#!/bin/bash

# Call the Python script and save its output to a .sql file
python3 python_query.py > output.sql

echo "SQL file generated: output.sql"