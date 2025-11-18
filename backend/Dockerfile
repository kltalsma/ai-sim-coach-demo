FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY demo_telemetry_generator.py .
COPY telemetry_readers/ ./telemetry_readers/

# Expose ports
EXPOSE 5001
EXPOSE 9996/udp
EXPOSE 9997/udp
EXPOSE 9998/udp
EXPOSE 9999/udp

# Run the application
CMD ["python", "main.py"]
