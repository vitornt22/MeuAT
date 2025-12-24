FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
	gdal-bin libgdal-dev g++ && \
	rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x start.sh

EXPOSE 8004
CMD ["bash", "start.sh"]