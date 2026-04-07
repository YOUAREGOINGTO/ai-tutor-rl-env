FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose port
EXPOSE 8000

# Run server from root so sys.path works correctly
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
