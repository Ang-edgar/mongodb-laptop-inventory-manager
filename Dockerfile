FROM fedora:39

WORKDIR /app

# Install Python and system dependencies
RUN dnf update -y && dnf install -y \
    python3 \
    python3-pip \
    gcc \
    python3-devel \
    && dnf clean all

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=__init__.py
ENV PYTHONPATH=/app

# Run the application
CMD ["python3", "__init__.py"]