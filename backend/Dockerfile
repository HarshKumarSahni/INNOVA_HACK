# 1. Use an official lightweight Python image
FROM python:3.12-slim

# 2. Python-specific optimizations for containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Install system dependencies for database drivers
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy requirements first (leverages Docker cache for faster builds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY . .

# 7. Create local storage directories
RUN mkdir -p data/generated_files data/raw_responses

# 8. Expose the deployment port
EXPOSE 10000

# 9. Run the application
# We use 0.0.0.0 so the server listens on all network interfaces
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
# Use shell format to expand the $PORT variable correctly
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]