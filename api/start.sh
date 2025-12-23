#!/bin/bash

# Roda o script como um módulo ou caminho direto
python scripts/seed.py

# Inicia o servidor
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload