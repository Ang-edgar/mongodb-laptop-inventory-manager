FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5001

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "app:app"]
