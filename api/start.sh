#!/bin/bash

# It Executes the script like a module or a direct path
python scripts/seed.py

# Starts server
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload