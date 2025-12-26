FROM python:3.10-slim

# Install system dependencies for geospatial data support (GDAL/OGR)
RUN apt-get update && apt-get install -y \
	gdal-bin libgdal-dev g++ && \
	rm -rf /var/lib/apt/lists/*

# Set environment variables for Python
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code into the container
COPY . .

# Expose the API port
EXPOSE 8004

# Default command to run the API
# Note: This will be overridden by docker-compose for the 'seed' and 'api' services
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]