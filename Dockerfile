# Use a lightweight Python image
FROM python:3.11-slim

# Set a working directory inside the container
WORKDIR /app



# Copy Python dependency file first to leverage docker layer caching
COPY requirements.txt .

# Install dependencies if requirements.txt exists
RUN pip install --no-cache-dir -r requirements.txt || true

# Copy the rest of your project files
COPY . .

VOLUME ["/app/data"]

# Default command to run your Python app
CMD ["python", "main.py"]
